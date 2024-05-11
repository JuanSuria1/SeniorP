import os
import smtplib
import ssl
from email.message import EmailMessage
import logging
import dotenv
import re
# we do this to check for possible invalid emails extensions
import pandas
import pandas as pd

df = pd.read_csv('blacklist.csv', header = None)
#print(df)
# df = data frame, is like a table in sql.
dotenv.load_dotenv()
# Uses information in a different .env file
email_sender = ''
email_password = ''
email_receiver = ''
# Initialize logging
logging.basicConfig(filename='email_sender_tls.log', level=logging.INFO)

# Function to load email credentials and server details from environment variables
def load_credentials():
     email_sender = os.getenv('EMAIL_SENDER', 'default_sender@gmail.com')
     email_password = os.getenv('EMAIL_PASSWORD', 'default_password')
     email_receiver = os.getenv('EMAIL_RECEIVER', 'default_receiver@gmail.com')
     smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
     port = int(os.getenv('SMTP_PORT', 587))
     return email_sender, email_password, email_receiver, smtp_server, port

# Function to validate email addresses

email_regex = re.compile(
     r"^(?!.*\.\.)(?!\.)[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*"
     r"@(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
)

def validate_email(email):
     # First step
     first = bool(email_regex.match(email))
     # Code to validate blacklist
     second = True # Default Value
     #checks for valid domains
     username, domain = email.split("@")
     result = df.isin([domain]).any()
     if result.any():
          second = False
     #False = Not pass the checkpoint
     return first and second #TRUE AND TRUE = TRUE   TRUE AND FALSE = FALSE

# Function to test SMTP connection via TLS
def test_smtp_connection(smtp_server, port):
     try:
          with smtplib.SMTP(smtp_server, port) as smtp:
               smtp.ehlo()
               smtp.starttls(context=ssl.create_default_context())  # Upgrade to a secure connection
               smtp.noop()
          logging.info("SMTP server connection (TLS) successful.")
     except Exception as e:
          logging.error(f"Failed to connect to SMTP server (TLS): {e}")
          print("Failed to connect to SMTP server (TLS).")
          exit(1)

# Function to send the email via TLS
def send_email(subject, body, ):
     email_sender, email_password, email_receiver, smtp_server, port = load_credentials()

     if not (validate_email(email_sender) and validate_email(email_receiver)):
          logging.error("Invalid email address.")
          raise ValueError("Invalid email address.")


     em = EmailMessage()
     em['From'] = email_sender
     em['To'] = email_receiver
     em['Subject'] = subject
     em.set_content(body)

     test_smtp_connection(smtp_server, port)

     try:
          with smtplib.SMTP(smtp_server, port) as smtp:
               smtp.ehlo()
               smtp.starttls(context=ssl.create_default_context())  # Start TLS encryption
               smtp.login(email_sender, email_password)
               smtp.send_message(em)
          logging.info("Email sent successfully using TLS.")
     except Exception as e:
          logging.error(f"Error sending email using TLS: {e}")
          print("Failed to send the email.")

# Main function to interact with the user
def main():
     subject = input("Enter the email subject: ")
     body = input("Enter the email body: ")
     send_email(subject, body)

if __name__ == "__main__":
     main()

