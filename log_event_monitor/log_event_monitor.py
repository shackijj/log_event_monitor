#!/usr/bin/python

import time
import os
from sys import argv
import sendmail
import re
import xml.etree.ElementTree as ET
import logging
from process import Process

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
        self.processes = []
        self.default_process_timeout = 10
        self.update_interval = 0.001
        self.get_config(filename)


    def get_config(self, root):
       
        pattern = root.find('pattern')
        if pattern is not None:
            self.pattern = re.compile(pattern.text)
        else:
            raise ConfigError("Pattern is not found in the %s" % filename)

        timeout = root.find('timeout')
        if timeout is not None:
            self.timeout = int(timeout.text)

        
        update_interval = root.find('UpdateInterval')
        if update_interval is not None:
            try:
                self.update_interval = float(update_interval.text) / 1000
            except ValueError:
                raise ConfigError("Update interval (ms) should be integer")

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

        self._process_on_event(root)

    def _process_on_event(self, root):

        on_events = root.findall('OnEvent')
        for on_event in on_events:

            command = on_event.find('command')
            if command is not None:
                command = command.text
            else:
                raise ConfigError("OnEvent doesn't have command")
            
                
            output_file = on_event.find('OutputFile')
            if output_file is not None:
               output_file = output_file.text
            else:
               raise ConfigError("OnEvent doesn't have OutputFile")

            send_output = on_event.find('SendOutput')
            if send_output is not None:
                if send_output.text.lower() == "true":
                    send_output = True
                else:
                    send_output = False
            else:
                send_output = False           

            process_timeout = on_event.find('ProcessTimeout')
            if process_timeout is not None:
                try:
                    process_timeout = int(process_timeout.text)
                except ValueError:
                    process_timout = self.default_process_timeout
            else:
                process_timeout = self.default_process_timeout
            
            new_process = Process(command, output_file, send_output, process_timeout)
            self.processes.append(new_process)


    def _start_all_processes(self):

        """
        We don't want to ruin whole application
        whether one subprocess is broken (i.e user saved 
        bad command in configuration).                          
        """
        broken_proc = None

        for proc in self.processes:
            try:
                proc.start()
            except OSError as e:
                msg = "Check command syntax %s " % proc.get_command()
                broken_proc = proc
                self.logger.error(msg)

        if broken_proc:
           self.processes.remove(broken_proc)
                               

    def _cleanup_all_processes(self):
        self.logger.info("Cleanup processes...")

        for proc in self.processes:
            pid = proc.get_pid()

            if proc.return_code() is None:
               self.logger.debug("Trying to kill process %s" % pid)
               proc.terminate()
    
            return_code = proc.wait()  
            self.logger.debug("%s return code is: %s" % (pid, return_code))
            proc.delete_output_file()

    def _get_files_array(self):

        result = []
        for proc in self.processes:
            if proc.send_output:
                result.append(proc.output_file)
        return result

    def run(self):

        buffer = ""
        timer = 0

        try:
            self.logger.debug("opening file %s" % self.log_file)
            with open(self.log_file) as fh:
                fh.seek(0, os.SEEK_END)
                
                while(1):

                    if not os.path.isfile(self.log_file):
                        raise IOError
                    
                    line = fh.readline()
                    while line:
                        if self.pattern.search(line): 
                            if timer == 0:
                                self._start_all_processes()
                                timer = time.time()

                            buffer += line
                        line = fh.readline()

                    if timer and ( time.time() - timer > self.timeout ):

                        self.logger.info("Sending mail...")
                        self.logger.debug(buffer)
                        files_array = self._get_files_array()

                        try:
                            self.mail_handler.sendmail_conf(buffer, files_array)
                        except Exception as e:
                            self.logger.error("Can't send mail error: %s" % e)

                        self._cleanup_all_processes()
                         
                        timer = 0
                        buffer = ""

                    time.sleep(self.update_interval)

        except IOError as e:
            self.logger.error("%s" % e)
            time.sleep(5)
            self.run()
