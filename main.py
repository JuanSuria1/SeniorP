import os
import smtplib
import ssl
from email.message import EmailMessage
import logging
import dotenv
import re
from csv_handler import CSVData

# Logging configuration
logging.basicConfig(filename='email_sender_tls.log', level=logging.INFO)

# Load environment variables from .env file
dotenv.load_dotenv()
email_sender = os.getenv('EMAIL_SENDER', 'default_sender@gmail.com')
email_password = os.getenv('EMAIL_PASSWORD', 'default_password')
email_receiver = os.getenv('EMAIL_RECEIVER', 'default_receiver@gmail.com')

# Function to load email credentials and SMTP server details from environment variables
def load_credentials():
     smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
     port = int(os.getenv('SMTP_PORT', 587))
     return smtp_server, port

# Regular expression to validate email addresses
email_regex = re.compile(
     r"^(?!.*\.\.)(?!\.)[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*"
     r"@(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
)

# Function to validate email addresses
def validate_email(email):
     if not email_regex.match(email):
          return False
     username, domain = email.split("@")
     # Check if the domain is in the blacklist
     df = CSVData('blacklist.csv', has_header=False)
     if df.exists(domain):
          return False
     return True

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
          raise

# Function to send the email via TLS
def send_email(subject, body):
     smtp_server, port = load_credentials()

     if not (validate_email(email_sender) and validate_email(email_receiver)):
          logging.error("Invalid email address.")
          raise ValueError("Invalid email address.")

     em = EmailMessage()
     em['From'] = email_sender
     em['To'] = email_receiver
     em['Subject'] = subject
     em.set_content(body)

     try:
          test_smtp_connection(smtp_server, port)
          with smtplib.SMTP(smtp_server, port) as smtp:
               smtp.ehlo()
               smtp.starttls(context=ssl.create_default_context())  # Start TLS encryption
               smtp.login(email_sender, email_password)
               smtp.send_message(em)
          logging.info("Email sent successfully using TLS.")
     except Exception as e:
          logging.error(f"Error sending email using TLS: {e}")
          raise

# Function to attach files
def attach_file(em, file_path):
     try:
          with open(file_path, 'rb') as f:
               file_data = f.read()
               file_name = os.path.basename(file_path)
          em.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)
          logging.info(f"Attached file '{file_name}' added to the email.")
     except FileNotFoundError:
          logging.error(f"File '{file_path}' not found.")
          raise
     except Exception as e:
          logging.error(f"Error attaching file '{file_path}': {e}")
          raise

# Function to send email with attachment via TLS
def send_email_with_attachment(subject, body, file_path):
     smtp_server, port = load_credentials()

     if not (validate_email(email_sender) and validate_email(email_receiver)):
          logging.error("Invalid email address.")
          raise ValueError("Invalid email address.")

     em = EmailMessage()
     em['From'] = email_sender
     em['To'] = email_receiver
     em['Subject'] = subject
     em.set_content(body)

     try:
          test_smtp_connection(smtp_server, port)
          with smtplib.SMTP(smtp_server, port) as smtp:
               smtp.ehlo()
               smtp.starttls(context=ssl.create_default_context())  # Start TLS encryption
               smtp.login(email_sender, email_password)
               attach_file(em, file_path)  # Attach file
               smtp.send_message(em)
          logging.info("Email with attachment sent successfully using TLS.")
     except Exception as e:
          logging.error(f"Error sending email with attachment using TLS: {e}")
          raise

# Main function to interact with the user
def main():
     try:
          subject = input("Enter the email subject: ")
          body = input("Enter the email body: ")

          # Ask the user if they want to attach a file
          attach_file_option = input("Do you want to attach a file? (y/n): ").strip().lower()
          if attach_file_option == 'y':
               file_path = input("Enter the path of the file to attach: ").strip()
               send_email_with_attachment(subject, body, file_path)
          else:
               send_email(subject, body)

          print("Email sent successfully!")
     except Exception as e:
          print(f"Error: {e}")

if __name__ == "__main__":
     main()