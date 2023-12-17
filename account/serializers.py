"""
Serializers for accounting api
"""
from rest_framework import serializers

from core.models import Accounting


class AccountingSerializer(serializers.ModelSerializer):
    """Serializer for accounting objects"""

    class Meta:
        model = Accounting
        fields = ('id', 'date', 'type', 'amount')
        read_only_fields = ('id',)


class AccountingDetailSerializer(AccountingSerializer):
    """Serialize a accounting detail"""

    class Meta(AccountingSerializer.Meta):
        fields = AccountingSerializer.Meta.fields
        read_only_fields = ('id',)