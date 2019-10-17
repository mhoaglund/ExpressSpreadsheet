from multiprocessing import Process

class InputSettings(object):
    """
        Args:
        Delay (double, portion of a second),
        Pin (int, io pin),
        Queue (job queue outgoing from input manager)
    """
    def __init__(self, _delay, _pin, _queue):
        self.delay = _delay
        self.trigger_pin = _pin
        self.trigger_queue = _queue

class QueuePayload(object):
    """
    """
    def __init__(self, row, stateflag):
        self.reading = row[1]
        self.timestamp = row[0]
        self.state = stateflag

class DataSettings(object):
    """
    """
    def __init__(self, _filename):
        self.filename = _filename

class OutputSettings(object):
    """
        Args:
        Domain (tuple with angle range for servo),
        Pin (int, io pin used for PWM to the servo),
        Queue (job queue incoming from input manager)
    """
    def __init__(self, _domain, _pin, _queue):
        self.domain = _domain
        self.trigger_pin = _pin
        self.trigger_queue = _queue

class IOManager(Process):
    """Process to handle GPIO input"""
    def __init__(self, _settings):
        import RPi.GPIO as GPIO
        super(IOManager, self).__init__()
        print('Starting Input Manager')
        GPIO.setmode(GPIO.BCM)
        self.cont = True
        self.trigger_pin = _settings.trigger_pin
        self.delay = _settings.delay
        self.trigger_queue = _settings.trigger_queue
        self.iostate = False
        GPIO.setup(self.trigger_pin, GPIO.IN)

    def run(self):
        while self.cont:
            state = GPIO.input(self.trigger_pin)
            if state == 1 and not self.iostate:
                self.iostate = True
                self.trigger()
            if state == 0 and self.iostate:
                self.iostate = False
    
    def stop(self):
        """Stop method called from parent"""
        print('terminating')
        self.cont = False
        GPIO.cleanup()

    def trigger(self):
        """Trigger state reached. Dump an event into the queue for parent to process."""
        self.trigger_queue.put(1)