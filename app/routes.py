from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, current_user
from . import db
from .models import User
from .forms import RegistrationForm, LoginForm, RecoveryForm, AutoTradingForm
from .utils import send_confirmation_email, send_recovery_email

@app.route('/')
def home():
    if current_user.is_authenticated:
        return render_template('home_logged_in.html')
    else:
        return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(
            name=form.name.data,
            surname=form.surname.data,
            date_of_birth=form.date_of_birth.data,
            email=form.email.data,
            username=form.username.data
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()

        send_confirmation_email(new_user.email)

        flash('Registration successful! Please check your email for confirmation.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/recover', methods=['GET', 'POST'])
def recover():
    form = RecoveryForm()
    if form.validate_on_submit():
        # Implement account recovery functionality...
        pass

    return render_template('recover.html', form=form)

@app.route('/portfolio')
def portfolio():
    # Fetch portfolio data using the Interactive Brokers API...
    return render_template('portfolio.html')


@app.route('/auto_trade', methods=['GET', 'POST'])
def auto_trade():
    if request.method == 'POST':
        stock_symbol = request.form['stock_symbol']
        stop_loss_fraction = float(request.form['stop_loss_fraction'])
        user_id = current_user.id

        # Perform auto-trading
        auto_trade(stock_symbol, user_id, stop_loss_fraction)

        flash('Auto-trading completed successfully!', 'success')
        return redirect(url_for('portfolio'))

    return render_template('auto_trade.html')
