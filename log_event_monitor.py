#!/usr/bin/python

from log_event_monitor.log_event_monitor import LogEventMonitor
import os

dir = os.path.dirname(__file__)
filename = os.path.join(dir, 'conf/config.xml')

app = LogEventMonitor(filename)
app.run()
