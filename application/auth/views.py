from flask import render_template, redirect, url_for, session, request, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import User
import flask_bcrypt
from flask_login import login_user, current_user, login_required
from . import auth
from ..forms import LoginForm, RegistrationForm
from .. import (login_manager, db)
from sqlalchemy.exc import IntegrityError
from flask_mail import Message, Mail
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

s = URLSafeTimedSerializer('ad40898f84d46bd1d109970e23c0360e')



mail = Mail()


def adduser(form, is_admin):
    hashed_password = generate_password_hash(form.Password.data)
    print(is_admin)
    if is_admin:
        user = User(username=form.username.data,
                    firstname=form.firstName.data,
                    lastname=form.lastName.data,
                    email=form.Email.data,
                    isadmin=True,
                    password=hashed_password,
                    confirmed=True)
        return user
    elif not is_admin:
        user = User(username=form.username.data,
                    firstname=form.firstName.data,
                    lastname=form.lastName.data,
                    email=form.Email.data,
                    isadmin=False,
                    password=hashed_password,
                    confirmed=True)
        return user
    else:
        return 'something was incorrect'




def send_email(form):
    token = s.dumps(form.Email.data)
    msg = Message('Confirm Email', sender='pitechcorp7@gmail.com', recipients=[form.Email.data])
    link = url_for('auth.confirm_email', token=token, _external=True)

    msg.body = ('Next step is to click the following link then you can start ordering with us. Your '
                'link is {}. We are really glad you choose us, remember the more you purchase the you increase your loyalty points, of which you can use later to buy free meals.').format(
        link)
    mail.send(msg)
    return token



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))                                                                                                                                 



@auth.route("/register", methods=["POST", "GET"])
def register():
    form = RegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            print("form successfully submitted for registration")
            hashed_password = flask_bcrypt.generate_password_hash(form.Password.data).decode(
                'utf-8')
            isadmin = form.option.data
            print(hashed_password, isadmin)
            users = User(username=form.username.data,
                             firstname=form.firstName.data,
                             lastname=form.lastName.data,
                             email=form.Email.data,
                             isadmin=False,
                             password=hashed_password)

            print("Adding...")
            db.session.add(users)
            try:
                db.session.commit()
            except IntegrityError:
                flash('Username or email already exist')
                return redirect(url_for('auth.register'))

            print("Done...")
            flash("Registration done, you can now login")
            return redirect(url_for('auth.newlogin'))

        else:
            flash("Failed to register")
            print("form failed to validate on submit")
            return redirect(url_for('auth.register'))
    return render_template('auth/register.html', form=form)


@auth.route('/newlogin', methods=['GET', 'POST'])
def newlogin():
    form = LoginForm()

    if form.validate_on_submit():
        if request.method == "POST":
            password = form.password.data
            email = form.email.data
            user = User.query.filter_by(email=email).first()
            if user and flask_bcrypt.check_password_hash(user.password, password):

                if user.isadmin:
                    login_user(user)
                    session["email"] = form.email.data
                    flash("Login Successful")
                    return redirect(url_for('admin.adminpage'))
                else:
                    login_user(user)
                    session["email"] = form.email.data
                    flash("Login Successful")
                    return redirect(url_for('main.home'))

            else:
                flash("Either Password or Email entered is be wrong")
                print("Either Password or Email entered is be wrong")
    return render_template('auth/newlogin.html', form=form)



def confirm_token(token, expiration=3600):
    try:
        email = s.loads(token, max_age=expiration)
        return email
    except Exception:
        return False


@auth.route('/confirm_email/<token>')
@login_required
def confirm_email(token):
    try:
        email = s.loads(token, max_age=5000)
        user_id = User.query.filter(email=email).first()

        user = User.query.get_or_404(user_id)
        if user:

            user.confirmed = True
            flash('Account was successfully confirmed')
            return redirect(url_for('auth.login'))
        else:
            flash('something went wroung')
            print('something went wrong'
            )
    except SignatureExpired:
        return '<h1>The token expired</h1>'
    return render_template('confirm_email')
        
@auth.route('/unconfirmed')
def unconfirmed():
    return render_template('auth/email/unconfirmed.html')
    

                                                                                                                                                                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                                                
