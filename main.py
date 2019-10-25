import os
import sys
import schedule
import subprocess
import logging
from multiprocessing import Queue
from datetime import datetime, time

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
    "/home/pi/ExpressSpreadsheet/sampled.csv"
)

DATA_PAGER = DataPager(DATA_SETTINGS)

PAUSED = False

PARAMS = [0,0]

def translate(value, leftMin, leftMax, rightMin, rightMax):
    if value < leftMin:
        value = leftMin
    if value > leftMax:
        value = leftMax
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin
    valueScaled = float(value - leftMin) / float(leftSpan)
    return int(rightMin + (valueScaled * rightSpan))

def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.utcnow().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time

def setup():
    #We get the last row because the datapager flips the CSV over.
    # PARAMS[0] = float(DATA_PAGER.last()[0])
    # PARAMS[1] = float(DATA_PAGER.last()[1])
    PARAMS[0] = 740
    PARAMS[1] = 800
    spinupoutputprocess()
    if is_time_between(time(9,00), time(17,00)):
        awake()
    else:
        asleep()
    return True

def spinupoutputprocess():
    """Activate serial port trigger"""
    if __name__ == '__main__':
        _hwmgr = HardwareController(OUTPUT_SETTINGS)
        PROCESSES.append(_hwmgr)
        _hwmgr.start()

def bracket(val, lowest, highest):
    _val = val
    if _val > highest:
        _val = highest
    if _val < lowest:
        _val = lowest
    return _val
    
def sendLatestData():
    # TODO get next data frame from datapager
    if not PAUSED:
        packet = DATA_PAGER.next()
        latest = QueuePayload(
            translate(
                float(packet[1]), 
                PARAMS[0], 
                PARAMS[1], 
                0, 
                180
                ), 
            packet[0],
            None)
        TRIGGERQUEUE.put(latest)
        print(latest.reading)
    return True

def awake():
    global PAUSED
    DATA_PAGER.restart()
    PAUSED = False
    TRIGGERQUEUE.put(QueuePayload(None, None, "On"))
    LOGGINGQUEUE.put("Starting program in the morning...")

def asleep():
    global PAUSED
    PAUSED = True
    TRIGGERQUEUE.put(QueuePayload(None, None, "Off"))
    LOGGINGQUEUE.put("Stopping program in the evening...")

def stopworkerthreads():
    """Stop any currently running threads"""
    global PROCESSES
    for proc in PROCESSES:
        proc.stop()
        proc.join()

schedule.every(12).seconds.do(sendLatestData)
schedule.every().day.at("09:00").do(awake)
schedule.every().day.at("17:00").do(asleep) 

if setup():
    logger.info("starting...")
try:
    sendLatestData()
    while True:
        schedule.run_pending()
        while not LOGGINGQUEUE.empty():
            logmsg = LOGGINGQUEUE.get()
            if logmsg is not None:
                logger.info(logmsg)
        x = 1
except (KeyboardInterrupt, SystemExit):
    stopworkerthreads()