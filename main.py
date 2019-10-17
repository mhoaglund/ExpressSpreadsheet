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
    "sampled.csv"
)

DATA_PAGER = DataPager(DATA_SETTINGS)

def getParamsFromPager():
    params = DATA_PAGER.first()
    #TODO send the max and min from the params over to outputmgr to calibrate
    return True
    
def sendLatestData():
    # TODO get next data frame from datapager
    latest = QueuePayload(DATA_PAGER.next(), None)
    TRIGGERQUEUE.put(QueuePayload(DATA_PAGER.next(), None))
    print(latest.reading)
    return True

def awake():
    TRIGGERQUEUE.put(QueuePayload(None, "On"))

def asleep():
    TRIGGERQUEUE.put(QueuePayload(None, "Off"))

def stopworkerthreads():
    """Stop any currently running threads"""
    global PROCESSES
    for proc in PROCESSES:
        proc.stop()
        proc.join()

schedule.every(12).seconds.do(sendLatestData)
schedule.every().day.at("08:00").do(awake)
schedule.every().day.at("16:00").do(asleep) 

if getParamsFromPager():
    print("starting...")
try:
    while True:
        schedule.run_pending()
        while not LOGGINGQUEUE.empty():
            logmsg = LOGGINGQUEUE.get()
            if logmsg is not None:
                print(logmsg)
        x = 1
except (KeyboardInterrupt, SystemExit):
    stopworkerthreads()