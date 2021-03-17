import smtplib

port = 587
smtp_server = smtplib.SMTP("smtp.gmail.com", port)
smtp_server.ehlo()
smtp_server.starttls()
smtp_server.ehlo
sender_email = "lenss@glaseducation.org"  # Enter your address
receiver_email = "joe.murphy1415@gmail.com"  # Enter receiver address
password = input("Type your password and press enter: ")
smtp_server.login(sender_email, password)
message = """\
Subject: Hi there

This message is sent from Python."""
smtp_server.sendmail(sender_email, receiver_email, message)
smtp_server.close()
