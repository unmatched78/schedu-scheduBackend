from django.core.mail import send_mail, BadHeaderError
from django.conf import settings

def send_authentication_email(get_started_instance):
    subject = "New Get Started Request"
    message = (
        f"Hello,\n\nA new user has filled out the 'Get Started' form:\n\n"
        f"First Name: {get_started_instance.first_name}\n"
        f"Last Name: {get_started_instance.last_name}\n"
        f"Phone: {get_started_instance.phone_number}\n"
        f"Email: {get_started_instance.email}\n"
        f"Message: {get_started_instance.message}\n\n"
        "Best regards,\nYour Quickask Team"
    )
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            ["iradukundavierra4@gmail.com"],  # Replace with your admin email or list
        )
        print("Email sent successfully.")
    except BadHeaderError:
        print("Invalid header found.")
    except Exception as e:
        print(f"An error occurred while sending email: {e}")
