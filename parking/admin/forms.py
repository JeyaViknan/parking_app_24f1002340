from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length


class ParkingLotForm(FlaskForm):
    prime_location_name = StringField("Prime Location Name", validators=[DataRequired(), Length(max=200)])
    price_per_hour = FloatField("Price per hour", validators=[DataRequired(), NumberRange(min=0)])
    address = StringField("Address", validators=[DataRequired(), Length(max=255)])
    pincode = StringField("Pincode", validators=[DataRequired(), Length(max=20)])
    max_spots = IntegerField("Maximum number of spots", validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField("Save")
