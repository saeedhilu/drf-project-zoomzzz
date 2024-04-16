# mixins.py

from rest_framework import serializers
from phonenumbers import parse as phonenumbers_parse, is_valid_number as phonenumbers_is_valid


class PhoneNumberMixin:
    """
    Mixin for phone number validation.
    """

    def validate_phone_number(self, value):
        try:
            parsed_number = phonenumbers_parse(value, None)
            if not phonenumbers_is_valid(parsed_number):
                raise serializers.ValidationError("Invalid phone number format")
        except Exception as e:
            raise serializers.ValidationError("Invalid phone number format")
        
        return value
