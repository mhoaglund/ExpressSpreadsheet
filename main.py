#TODO: omxplayer management

import os
import sys
import schedule
import subprocess
import logging
from multiprocessing import Queue

from datapager import DataPager
from helpers import DataSettings, QueuePayload, OutputSettings
from output import HardwareController

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

OUTPUT_SETTINGS = OutputSettings(
    4,
    23,
    27,
    TRIGGERQUEUE,
    LOGGINGQUEUE
)

DATA_SETTINGS = DataSettings(
    "sampled.csv"
)

DATA_PAGER = DataPager(DATA_SETTINGS)

PARAMS = [0,0]
HWMGR = None


def translate(value, leftMin, leftMax, rightMin, rightMax):
# Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin
    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)
    # Convert the 0-1 range into a value in the right range.
    return int(rightMin + (valueScaled * rightSpan))

def setup():
    #We get the last row because the datapager flips the CSV over.
    PARAMS[0] = float(DATA_PAGER.last()[0])
    PARAMS[1] = float(DATA_PAGER.last()[1])
    HWMGR = HardwareController(OUTPUT_SETTINGS)
    #TODO send the max and min from the params over to outputmgr to calibrate
    return True
    
def sendLatestData():
    # TODO get next data frame from datapager
    latest = QueuePayload(
        translate(
            float(DATA_PAGER.next()[1]), 
            PARAMS[0], 
            PARAMS[1], 
            0, 
            180
            ), 
        DATA_PAGER.next()[0],
         None)
    TRIGGERQUEUE.put(latest)
    print(latest.reading)
    return True

def awake():
    TRIGGERQUEUE.put(QueuePayload(None, None, "On"))

def asleep():
    TRIGGERQUEUE.put(QueuePayload(None, None, "Off"))

def stopworkerthreads():
    """Stop any currently running threads"""
    global PROCESSES
    for proc in PROCESSES:
        proc.stop()
        proc.join()

schedule.every(12).seconds.do(sendLatestData)
schedule.every().day.at("08:00").do(awake)
schedule.every().day.at("16:00").do(asleep) 

if setup():
    print("starting...")
try:
    sendLatestData()
    while True:
        schedule.run_pending()
        while not LOGGINGQUEUE.empty():
            logmsg = LOGGINGQUEUE.get()
            if logmsg is not None:
                print(logmsg)
        x = 1
except (KeyboardInterrupt, SystemExit):
    stopworkerthreads()