from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class RegistrationForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[DataRequired(), Length(min=2, max=100)]
    )

    email = StringField(
        "Email",
        validators=[DataRequired(), Email()]
    )

    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=6)]
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password")]
    )

    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[DataRequired(), Email()]
        )

    password = PasswordField(
        "Password",
        validators=[DataRequired()]
        )

    submit = SubmitField("Login")

class JobForm(FlaskForm):
        title = StringField(
            "Title",
            validators=[DataRequired(), Length(max=150)]
        )

        short_description = StringField(
            "Short Description",
            validators=[DataRequired(), Length(max=300)]
        )

        description = StringField(
            "Full Description",
            validators=[DataRequired()]
        )

        company = StringField(
            "Company",
            validators=[DataRequired(), Length(max=150)]
        )

        salary = StringField(
            "Salary",
            validators=[DataRequired(), Length(max=100)]
        )

        location = StringField(
            "Location",
            validators=[DataRequired(), Length(max=150)]
        )

        category = SelectField(
            "Category",
            coerce=int,
            validators=[DataRequired()]
        )

        submit = SubmitField("Add Job")

class ProfileForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[DataRequired(), Length(min=2, max=100)]
    )

    email = StringField(
        "Email",
        validators=[DataRequired(), Email()]
    )
    picture = FileField(
        "Update Profile Picture",
        validators=[FileAllowed(["jpg", "png", "jpeg"])]
    )


    submit = SubmitField("Update Profile")

class DeleteForm(FlaskForm):
    submit = SubmitField("Delete Job")