import re
from django.core.exceptions import ValidationError
from .models import User

def check_int(value, field):
    try:
        if int(value):
            raise ValidationError(
                f"{field} should not contain only numbers!")
    except ValueError: 
        return value

def validate_username(username):
    check_username = User.objects.filter(username=username)
    if check_username.exists():
        raise ValidationError("Username already exists!")
    check_int(username, "Username")
            
    return username

def validate_email(email):
    check_email = User.objects.filter(email=email)
    check_int(email, "Email")
    if check_email.exists():
        raise ValidationError(
            "User with this email already exists")

    elif re.search(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email) is None:
        raise ValidationError(
            "Please use a proper email format e.g janedoe@gmail.com")
    return email

def validate_login_email(email):
    check_email = User.objects.filter(email=email)
    check_int(email, "Email")
    
    if re.search(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email) is None:
        raise ValidationError(
            "Please use a proper email format e.g janedoe@gmail.com")
    elif not check_email.exists():
        raise ValidationError(
            "User with this email does not exist!")
    return email

def validate_password(password):
    check_int(password, "Password")
    if len(password) < 8 or len(password) == 0:
        raise ValidationError(
            "Password should contain atleast 8 characters")

    elif not password.isalnum():
        raise ValidationError(
            "Password should only contain letters and numbers")
    return password
