from flask_wtf import Form
from wtforms import SubmitField, StringField

class SearchForm(Form):
    title = StringField("Title")
    description1 = StringField("description1")
    description2 = StringField("description2")
    submit = SubmitField("Submit")