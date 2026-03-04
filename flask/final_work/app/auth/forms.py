from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, SubmitField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    ValidationError,
)

from app.models import User


class RegistrationForm(FlaskForm):
    username = StringField(
        "Имя пользователя",
        validators=[DataRequired(), Length(min=3, max=64)],
    )
    email = EmailField(
        "Email",
        validators=[DataRequired(), Email()],
    )
    password = PasswordField(
        "Пароль",
        validators=[DataRequired(), Length(min=8, message="Минимум 8 символов")],
    )
    password2 = PasswordField(
        "Повторите пароль",
        validators=[DataRequired(), EqualTo("password", message="Пароли не совпадают")],
    )
    submit = SubmitField("Зарегистрироваться")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("Это имя пользователя уже занято.")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Этот email уже зарегистрирован.")


class LoginForm(FlaskForm):
    email = EmailField(
        "Email",
        validators=[DataRequired(), Email()],
    )
    password = PasswordField(
        "Пароль",
        validators=[DataRequired()],
    )
    submit = SubmitField("Войти")
