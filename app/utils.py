from flask_mail import Message
from . import mail

def send_confirmation_email(email):
    msg = Message('Confirm your registration', recipients=[email])
    msg.body = 'Thank you for registering! Please confirm your email.'
    mail.send(msg)

def send_recovery_email(email, passcode):
    msg = Message('Account Recovery', recipients=[email])
    msg.body = f'Your recovery passcode is: {passcode}'
    mail.send(msg)
