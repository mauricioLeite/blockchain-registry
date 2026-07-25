import json
import logging


class JSONLogFormatter(logging.Formatter):
    
    def format(self, record):
        message = record.getMessage()
        try:
            info = json.loads(message)
        except (TypeError, ValueError):
            info = message

        payload = {
            "level": record.levelname,
            "file": record.module,
            "method": record.funcName,
            "infos": info,
        }
        return json.dumps(payload, ensure_ascii=False, default=str)
