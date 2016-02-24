#!/usr/bin/python

import os
import smtplib
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.MIMEBase import MIMEBase
from email.utils import COMMASPACE, formatdate
from email import Encoders
import xml.etree.ElementTree as ET

class SendMail(object):

    def __init__(self, config_file):
        self.server = "localhost"
        self.subject = ""
        self.send_from = ""
        self.send_to = []
        self.copy_to = []
        self.get_config(config_file)

    def get_config(self, config):

        root = ET.fromstring(config)
 
        server = root.find('server')
        if server is not None:
            self.server = server.text

        subject = root.find('subject')
        if subject is not None:
            self.subject = subject.text

        sendfrom = root.find('sendfrom')
        if sendfrom is not None:
            self.send_from = sendfrom.text

        for send_to in root.findall('sendto'):
            for address in send_to.findall('address'):
                self.send_to.append(address.text)

        for copy_to in root.findall('copyto'):
            for address in copy_to.findall('address'):
                self.copy_to.append(address.text)
            

    def sendmail_conf(self, text = "" , files=None):
        self.sendmail(self.send_from, self.send_to, self.copy_to, self.subject,
            text, files, self.server)

    def sendmail(self, send_from, send_to, copy_to, subject, text, files=None, server="localhost"):
        msg = MIMEMultipart()
        msg.add_header("From", send_from)
        msg.add_header("Date", formatdate(localtime=True))
        msg.add_header("To", COMMASPACE.join(send_to))
        msg.add_header("CC", COMMASPACE.join(copy_to))
        msg.add_header("Subject", subject)
        msg.attach(MIMEText(text))
    
        for f in files or []:
            with open(f, "rb") as fil:
    
                part = MIMEBase('application', "octet-stream")
                part.set_payload(fil.read())
                Encoders.encode_base64(part)
                part.add_header('Content-Disposition',
                    'attachment; filename="%s"' % os.path.basename(f)
                )
                msg.attach(part)
                fil.close()
    
        smtp = smtplib.SMTP(server)
        smtp.sendmail(send_from, send_to, msg.as_string())
        smtp.close()
