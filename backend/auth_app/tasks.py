import os 

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from email.mime.image import MIMEImage


def send_activation_email(email, activation_link):
    """
    Send email to activate account.
    """
    subject = 'Confirm your email'

    context = {
        "activation_link": activation_link,
    }
    
    html_message = render_to_string("auth_app/email_activation.html", context)
    plain_message = strip_tags(html_message)

    msg = EmailMultiAlternatives(
        subject,
        plain_message,
        from_email='info@videoFlix.com',
        to=[email]
    )
    msg.attach_alternative(html_message, "text/html")

    logo_path = os.path.join(settings.BASE_DIR, 'asserts', 'logo_icon.png')
    if os.path.exists(logo_path):
        with open(logo_path, 'rb') as img:
            image = MIMEImage(img.read())
            image.add_header('Content-ID', '<logo>')
            image.add_header('Content-Disposition', 'inline', filename='logo_icon.png')
            msg.attach(image)

    msg.send()
    
    
def send_passwordreset_email(email, passwordreset_link):
    """
    Send email to reset password.
    """
    subject = 'Reset your password'

    context = {
        "reset_link": passwordreset_link,
    }
    
    html_message = render_to_string("auth_app/email_reset.html", context)
    plain_message = strip_tags(html_message)

    msg = EmailMultiAlternatives(
        subject,
        plain_message,
        from_email='info@videoFlix.com',
        to=[email]
    )
    msg.attach_alternative(html_message, "text/html")

    logo_path = os.path.join(settings.BASE_DIR, 'asserts', 'logo_icon.png')
    if os.path.exists(logo_path):
        with open(logo_path, 'rb') as img:
            image = MIMEImage(img.read())
            image.add_header('Content-ID', '<logo>')
            image.add_header('Content-Disposition', 'inline', filename='logo_icon.png')
            msg.attach(image)

    msg.send()
    

