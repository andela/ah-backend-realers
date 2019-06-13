import re
from django.core.exceptions import ValidationError
from .models import Article
from authors.apps.authentication.validators import check_int

def validate_body(body):
    check_body = Article.objects.filter(body=body)
    if check_body.exists():
        raise ValidationError("Article with this body already exists!")
    
    check_int(body, "Body")
            
    return body

def check_title(value):
    check_int(value, "Title")
    return value

def check_desription(value):
    check_int(value, "Description")
    return value