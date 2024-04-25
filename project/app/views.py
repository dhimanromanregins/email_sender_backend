from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import SendEmail
from .serializers import SendEmailSerializer
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import os
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

import django
django.setup()



def send_dynamic_email(subject, name, email, price, mobile_number):
    # Construct HTML content with inline CSS
    html_content = """
    <!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Document</title>
    <style>
      * {
        font-family: sans-serif;
      }

      .payment-page {
        display: flex;
        justify-content: center;
      }

      .payment-info {
        padding: 5px;
        width: 50%;
      }

      .payment-info .logo {
        height: 3.25rem;
        width: 3.25rem;
        background-image: url(https://www.paypalobjects.com/paypal-ui/logos/svg/paypal-mark-color.svg) !important;
        background-position: center;
        background-size: cover;
        background-repeat: no-repeat;
        position: relative;
        margin-left: 25px;
      }

      .greeting span {
        color: blue;
      }

      .user-details {
        margin-left: 30px;
        margin-top: 20px;
      }

      .user-details .heading {
        font-size: 32px;
        color: #2222a5;
      }

      .user-details .sender-price,
      .user-details .due {
        margin: 20px 0px;
        font-size: 22px;
      }

      .user-data {
        margin-left: 32px;
      }

      .user-data .name {
        font-size: 20px;
        font-weight: bold;
      }

      .user-data .user-contact,
      .report {
        display: flex;
        gap: 8px;
        margin-top: 8px;
      }

      .user-data .user-contact svg {
        color: blue;
      }

      .user-data .user-contact .email {
        color: blue;
      }

      .invoice-details {
        margin-top: 65px;
      }

      .invoice-details .heading {
        font-size: 20px;
        color: #2222a5;
      }

      .invoice-details .amount,
      .invoice-details .seller-notes,
      .invoice-details .invoice-number {
        margin: 20px 0px;
      }

      .invoice-details .detail-heading {
        font-weight: bold;
      }

      .pay-invoice {
        margin: 40px 0;
        text-align: center;
      }

      .pay-invoice button {
        width: 50%;
        height: 50px;
        font-size: 18px;
        color: white;
        background: #1f1f93;
        font-weight: bold;
        border-radius: 25px;
        cursor: pointer;
      }

      .help-text .heading {
        font-size: 23px;
      }

      .help-text .report div {
        color: #1f1f93;
      }

      .help-text .text {
        text-align: justify;
        margin: 20px 0;
      }
    </style>
  </head>
  <body>
    <div class="payment-page">
      <div class="payment-info">
        <p class="greeting">Hello, <span>{}</span></p>
        <div class="logo"></div>
        <div class="user-details">
          <div class="heading">Here's your invoice</div>
          <div class="sender-price">
            Felipe Morton sent you an invoice for $299.00 USD
          </div>
          <div class="due">Due on receipt.</div>
          <div class="user-data">
            <div class="name">{}</div>
            <div class="user-contact">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                fill="currentColor"
                class="bi bi-phone-fill"
                viewBox="0 0 16 16"
              >
                <path
                  d="M3 2a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2zm6 11a1 1 0 1 0-2 0 1 1 0 0 0 2 0"
                />
              </svg>
              <div>{}</div>
            </div>
            <div class="user-contact">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                fill="currentColor"
                class="bi bi-envelope-fill"
                viewBox="0 0 16 16"
              >
                <path
                  d="M.05 3.555A2 2 0 0 1 2 2h12a2 2 0 0 1 1.95 1.555L8 8.414zM0 4.697v7.104l5.803-3.558zM6.761 8.83l-6.57 4.027A2 2 0 0 0 2 14h12a2 2 0 0 0 1.808-1.144l-6.57-4.027L8 9.586zm3.436-.586L16 11.801V4.697z"
                />
              </svg>
              <div class="email">freelance.iver.1.11@gmail.com</div>
            </div>
            <div class="user-contact">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                fill="currentColor"
                class="bi bi-file-text-fill"
                viewBox="0 0 16 16"
              >
                <path
                  d="M12 0H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2M5 4h6a.5.5 0 0 1 0 1H5a.5.5 0 0 1 0-1m-.5 2.5A.5.5 0 0 1 5 6h6a.5.5 0 0 1 0 1H5a.5.5 0 0 1-.5-.5M5 8h6a.5.5 0 0 1 0 1H5a.5.5 0 0 1 0-1m0 2h3a.5.5 0 0 1 0 1H5a.5.5 0 0 1 0-1"
                />
              </svg>
              <div>
                You don't have any payments with this seller in the last year.
              </div>
            </div>
          </div>
          <div class="invoice-details">
            <div class="heading">Invoice details</div>
            <div class="amount">
              <div class="detail-heading">Amount requested</div>
              <div>$299.00 USD</div>
            </div>
            <div class="seller-notes">
              <div class="detail-heading">Note from seller</div>
              <div>
                If you have any issue, do let us know +1(520)602-0210 sent you
                an invoice for $899.00 USD
              </div>
            </div>
            <div class="invoice-number">
              <div class="detail-heading">Invoice number</div>
              <div>0002</div>
            </div>
          </div>
        </div>
        <div class="pay-invoice">
          <button>View and Pay invoice</button>
        </div>
        <div class="help-text">
          <div class="heading">Don't recognize this invoice?</div>
          <div class="report">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="blue">
              <path
                d="M11.983 0a12.206 12.206 0 00-8.51 3.653A11.8 11.8 0 000 12.207 11.779 11.779 0 0011.8 24h.214A12.111 12.111 0 0024 11.791 11.766 11.766 0 0011.983 0zM10.5 16.542a1.476 1.476 0 011.449-1.53h.027a1.527 1.527 0 011.523 1.47 1.475 1.475 0 01-1.449 1.53h-.027a1.529 1.529 0 01-1.523-1.47zM11 12.5v-6a1 1 0 012 0v6a1 1 0 11-2 0z"
              ></path>
            </svg>
            <div>Report this invoice</div>
          </div>
          <div class="text">
            Before paying, make sure you recognize this invoice. If you don't,
            report it. Learn more about common security threats and how to spot
            them. For example, PayPal would never use an invoice or a money
            request to ask you for your account
          </div>
        </div>
      </div>
    </div>
  </body>
</html>

    """
    # html_content = html_content.format(email, name, mobile_number)
    template_name = 'email_template.html'
    context = {'name': name, 'email': email, 'mobile_number': mobile_number, 'price': price}
    rendered_string = render_to_string(template_name, context)

    # Create an EmailMultiAlternatives object to include both plain text and HTML content
    email = EmailMultiAlternatives(
        subject=subject,
        body="This is the plain text version.",
        from_email='sahildhiman98765@gmail.com',
        to=email,
    )

    # Attach the HTML content
    email.attach_alternative(rendered_string, "text/html")

    # Send email
    status = email.send()

    print(status, '=====')





class SendEmailList(APIView):
    def get(self, request, format=None):
        send_emails = SendEmail.objects.all()
        serializer = SendEmailSerializer(send_emails, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        for data in request.data:
            serializer = SendEmailSerializer(data=data)

            if serializer.is_valid():
                try:
                    serializer.save()
                    data = serializer.validated_data
                    # recipient_list = [data.get('recipient_list')]
                    name = data.get('name')
                    email = [data.get('email')]
                    price = data.get('price')
                    mobile_number = data.get('mobile_number')
                    print(data, '===========')
                    subject = "Test Email"
                    send_dynamic_email(subject, name, email, price, mobile_number)

                    # If email sent successfully, return success response

                except Exception as e:
                    # If an exception occurs during email sending, return error response
                    return Response({'email_sent': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'email_sent': True, 'message': 'Email sent successfully'}, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)