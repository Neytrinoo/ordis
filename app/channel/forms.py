from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField


class ChannelHeadForm(FlaskForm):
    image = FileField('Картинка', render_kw={'accept': 'image/*'})
    submit = SubmitField('Изменить оформление канала')
