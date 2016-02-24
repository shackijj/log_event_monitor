#!/usr/bin/python

from log_event_monitor.log_event_monitor import LogEventMonitor, ConfigError, XmlError
import xml.etree.ElementTree as ET
import os
from multiprocessing import Process
import logging

class LogEventMonitorApp(object):

    def __init__(self, config):
        self.monitors = []
        self.processes = []
        self.config_file_path = config
        self.get_config()

    def get_config(self):
        try:
            tree = ET.parse(self.config_file_path)
        except ET.ParseError as e:
            raise XmlError("Error in xml syntax: %s" % e)

        root = tree.getroot()

        for monitor_config in root.findall("LogEventMonitor"):
            monitor = LogEventMonitor(monitor_config)
            self.monitors.append(monitor)

    def create_processes(self):
        for monitor in self.monitors:
            proc = Process(target=monitor.run)
            self.processes.append(proc)

    def start_processes(self):
        for process in self.processes:
            process.start()
            
if __name__ == '__main__':

    dir = os.path.dirname(__file__)
    log_file_path = os.path.join(dir, "logs/log_event_monitor.log")
    config_file_path = os.path.join(dir, 'conf/config.xml')

    log = logging.getLogger("log_event_monitor")
    log.setLevel(logging.DEBUG)
    log_file_path = os.path.join(dir, "logs/log_event_monitor.log")
    log_fh = logging.FileHandler(log_file_path)
    formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(name)s - %(message)s')
    log_fh.setFormatter(formatter)
    log.addHandler(log_fh)
    log.info("log_event_monitor started.")

    try:
        app = LogEventMonitorApp(config_file_path)
        app.create_processes()
        app.start_processes()
    except XmlError as e:
        log.error("Check configuration: %s" % e)
        exit(2)
    except ConfigError as e:
        log.error("Wrong configuration: %s" % e)
        exut(3)
    except Exception as e:
        log.error("Unexpected error: %s" % e)
        exit(1)
