from rest_framework import serializers


class TransactionSerializer(serializers.Serializer):
    
    def to_internal_value(self, data):
        return data

    def validate(self, data):
        if not isinstance(data, dict) or not data:
            raise serializers.ValidationError("Transaction payload must be a non-empty JSON object.")
        return data

    def to_representation(self, instance):
        return instance
