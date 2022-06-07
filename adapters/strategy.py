from datetime import datetime
import logging, json

from django.db.models import F, QuerySet, Model, Count

from typing import Union

class StrategyModel():

    def __init__(self, model: Model) -> None:
        self.model = model

    def get(self, where: dict):
        result = self.model.objects.filter(**where).values()
        return result[0] if result else None
        
    def get_all(self):
        blocks = self.model.objects.all().values()
        return list(blocks) if blocks else []
    
    def last(self):
        result =  self.model.objects.last()
        return self.__clean_result(result)

    def count_rows(self):
        return self.model.objects.count()

    def insert(self, attrs: dict):
        print(attrs.__dict__, type(attrs.__dict__))
        new = self.model(**{"block": attrs.__dict__})
        new.save()
        return self.__clean_result(new)

    def __clean_result(self, result):
        result = result.__dict__
        del result['_state']
        return result

    # def get_all(self, where: dict = {}, select: list = None, **kwargs)  -> Union[list, None]:
    #     queryset = self.__evaluate_conditions(where, **kwargs)

    #     result = self._query_values(queryset, select, **kwargs)
    #     return list(result) if result else []

    def get(self, where: dict = {}, select: list = None, **kwargs) -> Union[dict, None]:
        element = self.get_all(where, select, **kwargs)
        return element[0] if element else None

    # def insert(self, attrs: Union[list, dict]) -> dict:
    #     if isinstance(attrs, dict):
    #         result = self.__insert_item(attrs)
    #     elif isinstance(attrs, list):
    #         result = [self.__insert_item(el) for el in attrs]

    #     return result

    # def update(self, where: dict, attrs: dict) -> Union[dict, None]:
    #     return self.__evaluate_conditions(where).update(**attrs)

    # def count_rows(self, where: dict) -> Union[dict, None]:
    #     return self.__evaluate_conditions(where).count()

    def delete(self, where: dict) -> Union[dict, None]:
        if hasattr(self.model, 'SOFT_DELETE') and self.model.SOFT_DELETE:
            result = self.update(where, { "deleted_at": datetime.now() })
        else:
            result = self.__evaluate_conditions(where).delete()
        
        if isinstance(result, tuple):
            return result[0]
        return result

    def increment_field(self, where: dict, field: str, increment: int = 1) -> bool:
        try:
            self.__evaluate_conditions(where).update(**{field:F(field)+increment})
            return True
        except Exception as error:
            logging.error(json.dumps({"error": str(error)}, ensure_ascii=False))
            return False

    def decrement_field(self, where: dict, field: str, decrement: int = 1) -> bool:
        try:
            self.__evaluate_conditions(where).update(**{field:F(field)-decrement})
            return True
        except Exception as error:
            logging.error(json.dumps({"error": str(error)}, ensure_ascii=False))
            return False

    def publish(self, where: dict, fields: list = []) -> bool:
        attrs = {
            "prod": F("homol"), 
            "published": 1, 
            "published_at": datetime.now()
        }
        
        for field in fields:
            attrs[field] = F(f"{field}_homol")
            
        try:
            return self.__evaluate_conditions(where).update(**attrs)
        except Exception as error:
            logging.error(json.dumps({"error": str(error)}, ensure_ascii=False))
            return False

    def __evaluate_conditions(self, where: dict, **kwargs) -> QuerySet:
        where, exclude = self._setup_where(where)
        queryset = self.model.objects.filter(**where)
        if exclude:
            queryset = queryset.exclude(**exclude)
        if "order_by" in kwargs:
            queryset = queryset.order_by(kwargs["order_by"])
        return queryset
    
    def _setup_where(self, where: dict) -> dict:
        conditions = {"where":{}, "exclude":{}}

        for key, value in where.items():
            op = "where"
            multi_cond = isinstance(value, list) and len(value) > 1 and isinstance(value[0], tuple)
            
            if multi_cond:
                for el in value:
                    op, m_key, value = self.__get_operation(key, el)
                    conditions[op][m_key] = value
                continue

            if isinstance(value, tuple):
                op, key, value = self.__get_operation(key, value)

            key = f"{key}__in" if isinstance(value, list) and not multi_cond else key
            
            conditions[op][key] = value
        return conditions["where"], conditions["exclude"]
    
    def __get_operation(self, key: str, value: tuple) -> tuple:
        return {
            "!=": ("exclude", key, value[1]),
            ">": ("where", f"{key}__gt", value[1]),
            ">=": ("where", f"{key}__gte", value[1]),
            "<": ("where", f"{key}__lt", value[1]),
            "<=": ("where", f"{key}__lte", value[1]),
            "*%": ("where", f"{key}__startswith", value[1]),
            "%*": ("where", f"{key}__endswith", value[1]),
            "!*": ("exclude", f"{key}__contains", value[1]),
            "%=": ("where", f"{key}__icontains", value[1]),
            "null": ("where", f"{key}__isnull", value[1])
        }[value[0]]

    def _query_values(self, queryset: QuerySet, select: list = None, **kwargs):
        if select or "group_by" in kwargs:
            select = select if select else kwargs["group_by"]
            
            if not isinstance(select, list):
                select = [select]
            result = queryset.values(*select)

            if "group_by" in kwargs:
                result = result.annotate(total=Count(kwargs["group_by"]))
            return result
        return queryset.values()

    def __insert_item(self, attrs: dict) -> dict:
        new_entry = self.model(**attrs)
        new_entry.save()
        result = new_entry.__dict__
        del result['_state']
        return result