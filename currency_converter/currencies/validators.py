from django.core.exceptions import ValidationError


def validate_currency_symbol(value):
    if not value.isupper():
        raise ValidationError("You must use only uppercase letters!")
