from multiprocessing import Process

class QueuePayload(object):
    """
    """
    def __init__(self, _reading, _timestamp, stateflag):
        self.reading = _reading
        self.timestamp = _timestamp
        self.state = stateflag

class DataSettings(object):
    """
    """
    def __init__(self, _filename):
        self.filename = _filename

class OutputSettings(object):
    """
        Args:
        Pin (int, io pin used for PWM to the servo),
        Queue (job queue incoming from input manager)
    """
    def __init__(self, _pin, _pump_pin, _override, _queue, _logqueue):
        self.servo_pin = _pin
        self.pump_pin = _pump_pin
        self.override = _override
        self.trigger_queue = _queue
        self.logging_queue = _logqueue
