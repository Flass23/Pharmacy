from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, MultipleFileField
from wtforms import StringField, FloatField, PasswordField, SubmitField, BooleanField, validators, TextAreaField, IntegerField,SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from application import *


class UpdateForm(FlaskForm):
    firstName = StringField('Firstname',
                            validators=[
                                Length(min=4, max=16)])
    lastName = StringField('Lastname',
                           validators=[
                               Length(min=4, max=16)])
    Email = StringField('Email',
                        validators=[
                            Length(min=5, max=30)])
    picture = FileField('Profile Picture')
    submit = SubmitField('Update')

class Search(FlaskForm):
    keyword = StringField('keyword')
    submit = SubmitField('Search')


class RegistrationForm(FlaskForm):
    username = StringField("Username",
                           validators=[DataRequired(), Length(min=3, max=18)])
    firstName = StringField('Firstname',
                            validators=[DataRequired(),
                                        Length(min=2, max=16)])
    lastName = StringField('Lastname',
                           validators=[DataRequired(),
                                       Length(min=2, max=16)])
    option = BooleanField("Admin?")

    Email = StringField('Email',
                        validators=[DataRequired(),
                                    Length(min=5, max=30)])

    Password = PasswordField('Password',
                             validators=[DataRequired()])

    submit = SubmitField('Register')



class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Length(min=5, max=30)])
    password = PasswordField('Password',
                             validators=[DataRequired()])

    submit = SubmitField('Login')


class BusinessForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired(), Length(min=5, max=120)])
    picture = FileField('Upload Picture', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'])])
    submit = SubmitField("Post")


class CartlistForm(FlaskForm):
    submit = SubmitField('AddtoCart')


class removefromcart(FlaskForm):
    submit = SubmitField("-")


class clearcart(FlaskForm):
    submit = SubmitField('Clear Cart')

class addmore(FlaskForm):
    submit = SubmitField("+")

class update(FlaskForm):

    newname = StringField("New Name")
    newprice = FloatField("New Price: ")
    quantity = IntegerField("Quantity")
    newdescription = StringField("New Description: ")
    picture = FileField('Upload Product Picture', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'])])
    category = TextAreaField("How to use")
    submit = SubmitField("Commit Update")


class confirmpurchase(FlaskForm):
    payment = SelectField("Payment Method", validators=[DataRequired()], choices=[('Cash', 'Cash'), ('Mpesa', 'Mpesa'),
                                                                           ('Ecocash', 'Ecocash')])
    transid = StringField('TransactionID')
    drop_address = StringField('Address For Collection')
    submit = SubmitField("Buy Cart")


class ProductForm(FlaskForm):
    product_name = StringField("Product Name", validators=[DataRequired()])
    product_description = StringField("Description", validators=[DataRequired()])
    product_quantity = IntegerField("Quantity",  validators=[DataRequired()])
    product_price = FloatField("Price", validators=[DataRequired()])
    product_pictures = FileField('Upload Product Picture', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'])])
    product_usage = TextAreaField("How to use", validators=[DataRequired()])
    submit = SubmitField("Add Product")


class updatestatusform(FlaskForm):
    status = SelectField('Status', validators=[DataRequired()], choices=[
                                                                         ('Pending', 'Pending'), ('Ready', 'Ready'),
                                                                ('Received', 'Received')])
    submit = SubmitField('Update Status')




