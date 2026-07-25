from rest_framework import serializers

from .block import canonical_timestamp


class BlockSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    index = serializers.IntegerField()
    transaction = serializers.JSONField()
    previous_hash = serializers.CharField()
    nonce = serializers.IntegerField()
    hash = serializers.CharField()
    created_at = serializers.SerializerMethodField()

    def get_created_at(self, obj):
        value = obj['created_at'] if isinstance(obj, dict) else obj.created_at
        return canonical_timestamp(value)
