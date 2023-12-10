"""
Serializers for the user API View
"""

from django.contrib.auth import (get_user_model, authenticate)
from django.utils.translation import gettext as _

from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""
    password_verify = serializers.CharField(write_only=True, min_length=5)

    class Meta:
        model = get_user_model()
        fields = ('account', 'password', 'password_verify', 'email', 'name')
        extra_kwargs = { 'password': { 'write_only': True, 'min_length': 5 }, }

    def validate(self, data):
        """Check that the two password fields match"""
        password_verify = data.pop('password_verify', None)
        if 'password' in data and password_verify is not None:
            if data['password'] != password_verify:
                raise serializers.ValidationError("Passwords must match")
        return data

    def create(self, validated_data):
        """Create and return a user with encrypted password"""
        validated_data.pop('password_verify', None)
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return a user """
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user

class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token"""
    account = serializers.CharField()
    password = serializers.CharField(
        style={ 'input_type': 'password' },
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        account = attrs.get('account')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=account,
            password=password,
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs