#TODO: omxplayer management

import os
import sys
import schedule
import subprocess
import logging
from multiprocessing import Queue

from datapager import DataPager
from helpers import IOManager, InputSettings, DataSettings, QueuePayload

from logging.handlers import RotatingFileHandler
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')

logger = logging.getLogger("Rotating Log")
logger.setLevel(logging.INFO)

handler = RotatingFileHandler('app.log', maxBytes=55500,
                                  backupCount=5)

handler.setFormatter(formatter)
logger.addHandler(handler)

PROCESSES = []
TRIGGERQUEUE = Queue()
LOGGINGQUEUE = Queue()

INPUT_SETTINGS = InputSettings(
    25,
    22,
    TRIGGERQUEUE
)

DATA_SETTINGS = DataSettings(
    "data.csv"
)

DATA_PAGER = None

schedule.every(30).seconds.do(sendLatestData)
schedule.every().day.at("08:00").do(awake)
schedule.every().day.at("16:00").do(asleep) 

def checkHWstate():
    DATA_PAGER = DataPager(DATA_SETTINGS)
    return True
    
def sendLatestData():
    # TODO get next data frame from datapager
    TRIGGERQUEUE.put(QueuePayload(DATA_PAGER.next(), None))
    return True

def awake():
    TRIGGERQUEUE.put(QueuePayload(None, "On"))

def asleep():
    TRIGGERQUEUE.put(QueuePayload(None, "Off"))

def spinupinput():
    """Activate GPIO trigger"""
    if __name__ == '__main__':
        _inputmgr = IOManager(INPUT_SETTINGS)
        PROCESSES.append(_inputmgr)
        _inputmgr.start()

def stopworkerthreads():
    """Stop any currently running threads"""
    global PROCESSES
    for proc in PROCESSES:
        proc.stop()
        proc.join()

if checkHWstate():
    spinupinput()
try:
    while True:
        while not LOGGINGQUEUE.empty():
            logmsg = LOGGINGQUEUE.get()
            if logmsg == "reboot":
                logger.info('Caught an omxplayer failure. Rebooting...')
                os.system("sudo reboot now -h")
            else:
                logger.info('Media Manager Report: ' + logmsg)
        x = 1
except (KeyboardInterrupt, SystemExit):
    stopworkerthreads()