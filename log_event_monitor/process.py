#!/usr/bin/python

import subprocess, shlex
import os
import logging

class Process(object):

    def __init__(self, command, output_file=None, 
        send_output=False, timeout=10):
        self.command = command
        self.output_file = output_file
        self.send_output = send_output
        self.timeout = timeout
        self.process = None
        self.output_file_handler = None
        self.logger = logging.getLogger("log_event_monitor.Process")

    def start(self):

        args = shlex.split(self.command) 
        self.output_file_handler = open(self.output_file, "w+")
                
        self.process = subprocess.Popen(args, 
           stderr=subprocess.STDOUT,
           stdout=self.output_file_handler)
            
    def get_command(self):
        return self.command    
            
    def close_file_handler(self):
        close(self.output_file_handler)
      
    def delete_output_file(self):

        try:
            if self.output_file_handler:
                self.output_file_handler.close()

            os.remove(self.output_file)
        except OSError as e:
           self.logger.error("OS Error: %s" % e)
        except IOError as e:
           self.logger.error("IO Error: %s" % e)

    def wait(self):
        return self.process.wait()

    def return_code(self):
        return self.process.poll()

    def terminate(self):
        self.process.terminate()

    def get_pid(self):
        return self.process.pid
