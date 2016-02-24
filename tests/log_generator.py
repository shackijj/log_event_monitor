#!/usr/bin/python
import random
import string
import logging

log = logging.getLogger("log_event_monitor")
log.setLevel(logging.DEBUG)

log_fh = logging.FileHandler('test.log')

formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(name)s - %(message)s')
log_fh.setFormatter(formatter)
log.addHandler(log_fh)
log.info("log_event_monitor started.")

 
while(1):
    len = random.randrange(0, 5000)
    str = ''.join(random.choice(string.ascii_lowercase) for o in range (len))
    if (len % 2):
        log.info('kernel')
        print "Event!!"
    log.info(str)
