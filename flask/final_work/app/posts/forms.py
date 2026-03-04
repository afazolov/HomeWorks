from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class PostForm(FlaskForm):
    title = StringField(
        "Заголовок",
        validators=[DataRequired(), Length(min=3, max=200)],
    )
    body = TextAreaField(
        "Текст поста",
        validators=[DataRequired(), Length(min=10)],
    )
    submit = SubmitField("Сохранить")
