import smtplib
from email.mime.text import MIMEText
import time 

sender_email = 'willholden9@gmail.com'
app_password = 'classified'  # Use the app password generated from Google
recipient_number = '6177773869'
carrier_gateway = 'vtext.com'  # Replace with the carrier's SMS gateway domain

with open("/home/pi/wnba_predictions/message_body.txt") as f:
    msg_body = f.read()

games = msg_body.split("***")



for game in games:
    if len(game) > 2:
        server = smtplib.SMTP('smtp.gmail.com', '587')
        server.starttls()
        server.login(sender_email, app_password)

        msg = MIMEText(game)
        msg['From'] = sender_email
        msg['To'] = f"{recipient_number}@{carrier_gateway}"

        server.sendmail(sender_email, [msg['To']], msg.as_string())

        print("Message sent!")
        server.quit()
        time.sleep(65)
