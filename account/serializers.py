"""
Serializers for accounting api
"""
from rest_framework import serializers

from core.models import Accounting, Category, MonthTarget, SaveMoneyTarget


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for category objects"""

    class Meta:
        model = Category
        fields = ('id', 'name')
        read_only_fields = ('id',)


class AccountingSerializer(serializers.ModelSerializer):
    """Serializer for accounting objects"""
    category = CategorySerializer(many=True, required=False)

    class Meta:
        model = Accounting
        fields = ('id', 'date', 'type', 'amount', 'category', 'title')
        read_only_fields = ('id',)

    def _get_or_create_category(self, categories, instance):
        auth_user = self.context['request'].user
        for category in categories:
            cate_obj, _ = Category.objects.get_or_create(user = auth_user, **category)
            instance.category.add(cate_obj)

    def create(self, validated_data):
        """Create a new accounting"""
        categories = validated_data.pop('category', [])
        accounting = Accounting.objects.create(**validated_data)
        self._get_or_create_category(categories, accounting)

        return accounting

    def update(self, instance, validated_data):
        '''Update a accounting'''
        categories = validated_data.pop('category', None)
        if categories is not None:
            instance.category.clear()
            self._get_or_create_category(categories, instance)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance


class AccountingDetailSerializer(AccountingSerializer):
    """Serialize a accounting detail"""

    class Meta(AccountingSerializer.Meta):
        fields = AccountingSerializer.Meta.fields + ('description',)
        read_only_fields = ('id',)


class MonthTargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthTarget
        fields = ['id', 'year', 'month', 'income', 'outcome']
        read_only_fields = ('id',)

class SaveMoneyTargetSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all()
    )

    class Meta:
        model = SaveMoneyTarget
        fields = ['id', 'category', 'target']
        read_only_fields = ('id',)


