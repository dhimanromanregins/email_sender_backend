import os
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

import django
django.setup()


def send_dynamic_email(subject, recipient_list, name, email, price, mobile_number):
    # Construct HTML content with inline CSS
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Email Template</title>
        <style>
            /* Your CSS styles here */
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #fff;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #007bff;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Hello, {name}!</h1>
            <p>Your email: {email}</p>
            <p>Price: {price}</p>
            <p>Mobile Number: {mobile_number}</p>
        </div>
    </body>
    </html>
    """

    # Create an EmailMultiAlternatives object to include both plain text and HTML content
    email = EmailMultiAlternatives(
        subject=subject,
        body="This is the plain text version.",
        from_email='sahildhiman98765@gmail.com',
        to=recipient_list,
    )

    # Attach the HTML content
    email.attach_alternative(html_content, "text/html")

    # Send email
    email.send()


subject = "Test Email"
recipient_list = ["sahildhiman98765@gmail.com"]
name = "John Doe"
email = "johndoe@example.com"
price = "$100"
mobile_number = "123-456-7890"


send_dynamic_email(subject, recipient_list, name, email, price, mobile_number)
