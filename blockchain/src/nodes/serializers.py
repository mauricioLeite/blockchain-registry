import re

from rest_framework import serializers

from blockchain.libraries.block import parse_timestamp

_HOST_PORT_RE = re.compile(r'^[A-Za-z0-9.\-]+:\d{1,5}$')
_HEX64_RE = re.compile(r'^[0-9a-f]{64}$')


class NodeAddressSerializer(serializers.Serializer):
    
    node_address = serializers.CharField()

    def validate_node_address(self, value):
        if not _HOST_PORT_RE.match(value):
            raise serializers.ValidationError("node_address must be in the form host:port.")
        return value


class BlockSyncSerializer(serializers.Serializer):

    id = serializers.IntegerField(required=False)
    index = serializers.IntegerField(min_value=1)  # genesis (index 0) is never synced this way
    transaction = serializers.JSONField()
    previous_hash = serializers.RegexField(_HEX64_RE)
    nonce = serializers.IntegerField(min_value=0)
    hash = serializers.RegexField(_HEX64_RE)
    created_at = serializers.CharField()

    def validate_created_at(self, value):
        try:
            parse_timestamp(value)
        except (TypeError, ValueError):
            raise serializers.ValidationError("created_at must be a parseable timestamp.")
        return value
