#!/usr/bin/python

import time
import os
from sys import argv
import sendmail
import re
import xml.etree.ElementTree as ET
import logging

class LogEventMonitorError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
      
class ConfigError(LogEventMonitorError): pass
class XmlError(LogEventMonitorError): pass
class LEMRuntimeError(LogEventMonitorError): pass

class LogEventMonitor(object):

    def __init__(self, filename):
        self.logger = logging.getLogger("log_event_monitor.LogEventMonitor")
        self.logger.debug("creating instance of LogEventMonitor")

        self.mail_handler = None
        self.pattern = r""
        self.log_file = ""
        self.timeout = 1

        self.get_config(filename)


    def get_config(self, filename):
    
        try:
            tree = ET.parse(filename)
        except IOError as e:
            raise ConfigError("File handling error: %s" % e)
        except ET.ParseError as e:
            raise XmlError("Error in xml syntax: %s" % e)
      
        root = tree.getroot()
    
        pattern = root.find('pattern')
        if pattern is not None:
            self.pattern = re.compile(pattern.text)
        else:
            raise ConfigError("Pattern is not found in the %s" % filename)

        timeout = root.find('timeout')
        if timeout is not None:
            self.timeout = int(timeout.text)

        log_file = root.find('logfile')
        if log_file is not None:
            self.log_file = log_file.text        
        else:
            raise ConfigError("Log file is no spicified in %s" % filename)

        mailconfig = root.find('mailconfig')
        if mailconfig is not None:
            mailconfig_str = ET.tostring(mailconfig)
            self.mail_handler = sendmail.SendMail(mailconfig_str)
        else:
            raise ConfigError("Mailconfig is not found in %s" % filename)

    def run(self):

        buffer = ""
        timer = 0

        try:
            self.logger.debug("opening file %s" % self.log_file)
            with open(self.log_file) as fh:
                fh.seek(0, os.SEEK_END)
                
                while(1):
                  
                    line = fh.readline()
                    if self.pattern.search(line):
                        buffer += line
    
                        if timer == 0:
                            timer = time.time()
    
                    if timer and ( time.time() - timer > self.timeout ):
                        self.mail_handler.sendmail_conf(buffer)
                        timer = 0
                        buffer = ""

                    time.sleep(0.001)

        except IOError as e:
            raise LEMRuntimeError("Can't handle log file %s" % e)
