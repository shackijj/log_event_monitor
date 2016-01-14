#!/usr/bin/python

import time
import os
from sys import argv
import sendmail
import re
import xml.etree.ElementTree as ET

class LogEventMonitor(object):

    def __init__(self, filename):
        self.mail_handler = None
        self.pattern = r""
        self.log_file = ""
        self.timeout = 1

        self.get_config(filename)


    def get_config(self, filename):
    
        tree = ET.parse(filename)
        root = tree.getroot()
    
        pattern = root.find('pattern')
        if pattern is not None:
            self.pattern = pattern.text

        timeout = root.find('timeout')
        if timeout is not None:
            self.timeout = int(timeout.text)

        log_file = root.find('logfile')
        if log_file is not None:
            self.log_file = log_file.text        

        mailconfig = root.find('mailconfig')
        if mailconfig is not None:
            mailconfig_str = ET.tostring(mailconfig)
            self.mail_handler = sendmail.SendMail(mailconfig_str)

    def run(self):

        buffer = ""
        timer = 0

        with open(self.log_file) as fh:
            fh.seek(0, os.SEEK_END)
            
            while(1):
              
                line = fh.readline()
                if re.search(self.pattern, line):
                    buffer += line

                    if timer == 0:
                        timer = time.time()

                if timer and time.time() - timer > self.timeout:
                    self.mail_handler.sendmail_conf(buffer)
                    timer = 0
                    buffer = ""

                time.sleep(0.001)
