#!/usr/bin/python

import smtplib
import os

sender = 'arun@estrrado.com'
receivers = ['benjamin@estrrado.com']
message = """From: Arun <arun@estrrado.com>
To: Benjamin <benjamin@estrrado.com>
Subject: Chronos Issue Notifier

Please note : A possible lock in the Chronos system has been detected.
"""
try:
     smtpObj = smtplib.SMTP('mail.estrrado.com', 26)
     smtpObj.sendmail(sender, receivers, message)
     os.system("""echo "Lock state detected in Chronos" | mail -s "Chronos Issue Notifier2" thebenonlyn@gmail.com""")
except:
     print "Error: unable to send email"

     
