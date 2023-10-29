from flask import Blueprint, current_app, flash, render_template
from flask_wtf import FlaskForm
from wtforms import EmailField, StringField, SubmitField
from wtforms.validators import DataRequired, Email

from web_app.models import Users
from web_app.spreadsheet import Spreadsheet


class UserForm(FlaskForm):
    """Form for adding a user"""

    user_name = StringField("Username", validators=[DataRequired()])
    email = EmailField("Email", validators=[Email()])
    submit = SubmitField("Add User")


bp = Blueprint("user", __name__, url_prefix="/user")


@bp.route("/new", methods=["GET", "POST"])
def new_user():
    """Add a new user"""
    users: Users = current_app.config["USERS"]
    spreadsheet: Spreadsheet = current_app.config["SPREADSHEET_OBJ"]
    form = UserForm()
    if form.validate_on_submit():
        if form.user_name.data and form.email.data:
            new_user = users.add_user(form.user_name.data, form.email.data)
            spreadsheet.create_spreasheet(new_user.user_id)
            spreadsheet.share_spreasheet(form.email.data)

            flash('User "{}" added.'.format(new_user.user_name))

            return render_template(
                "success.html",
                user_name=new_user.user_name,
                user_email=new_user.user_email,
                user_id=new_user.user_id,
            )
    return render_template("new_user.html", form=form)
