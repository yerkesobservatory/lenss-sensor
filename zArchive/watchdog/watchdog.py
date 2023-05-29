from datetime import datetime
import configparser
import os
import smtplib
import ssl
import sys

Password_FilePathName = sys.argv[2]
readPassword = configparser.ConfigParser()
readPassword.read(Password_FilePathName)

port = 465
password = readPassword["email"]["password"]
smtp_server = "smtp.gmail.com"
sender = "lenssserver@gmail.com"
receivers = ["joe.murphy1415@gmail.com", "adam@glaseducation.org"]

Config_FilePathName = sys.argv[1]
config = configparser.ConfigParser()
config.read(Config_FilePathName)

context = ssl.create_default_context()


def sendstatus():
    now = datetime.now()
    filename = now.strftime(config["arddatalogger"]["outfilename"])
    try:
        lastmodified = os.stat(filename).st_mtime
    except:
        lastmodified = 0
    datetime.fromtimestamp(lastmodified)
    UnixNow = now.timestamp()
    timeDelta = UnixNow - lastmodified

    message = """\
    Subject: Daily Status Report

    It has been %d second(s) since %s has been updated.""" % (
        timeDelta,
        filename,
    )

    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender, password)
        for address in receivers:
            server.sendmail(sender, address, message)


sendstatus()
