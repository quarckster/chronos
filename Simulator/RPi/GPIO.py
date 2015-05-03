import multiprocessing

IN = 1
OUT = 0
HIGH = True
LOW = False
PUD_OFF = 0
PUD_DOWN = 1
PUD_UP = 2
UNKNOWN = -1
BOARD = 10
BCM = 11

SERIAL = 40
SPI = 41
I2C = 42
PWM = 43

RISING = 31
FALLING = 32
BOTH = 33

REV = 0  # Board revision less than 2.0
#REV = 1  # Board revision 2.0 and above

# local part 
_debug = True
_gpiomode = UNKNOWN;

_pintogpio = [
    [-1, -1, -1, 0, -1, 1, -1, 4, 14, -1, 15, 17, 18, 21, -1, 22, 23, -1, 24, 10, -1, 9, 25, 11, 8, -1, 7],
    [-1, -1, -1, 2, -1, 3, -1, 4, 14, -1, 15, 17, 18, 27, -1, 22, 23, -1, 24, 10, -1, 9, 25, 11, 8, -1, 7]
]

_direction = [-1 for _ in range(0,54)]
_state = [False for _ in range(0,54)]

# communicate with remote side
def _read_state(channel):
    if _debug:
        print(_direction)
        print(_state)

    return _state[channel]

def _write_state(channel, val):
    _state[channel] = val
    if _debug:
        print(_direction)
        print(_state)

def _cleanup():
    global _direction
    global _state

    _direction = [-1 for _ in range(0,54)]
    _state = [0 for _ in range(0,54)]
    if _debug:
        print(_direction)
        print(_state)

def _get_channel(channel):
    if _gpiomode == BOARD:
        channel = _pintogpio[REV][channel]

    return channel

# Public interface
def setmode(mode):
    global _gpiomode
    if mode in [BOARD,BCM]:
        _gpiomode = mode
    else:
        raise Exception('InvalidModeException')
    return

def getmode():
    return _gpiomode

def setup(channel, inout, pull_up_down=PUD_OFF):
    global _direction
    global _gpiomode
    global _pintogpio

    if _gpiomode == UNKNOWN:
        print("Set mode first!")
        raise Exception('InvalidModeException')
    elif _gpiomode == BOARD:
        channel = _pintogpio[REV][channel]

    _direction[channel] = inout
    if _debug:
        print(_direction)
    return None

def cleanup():
    _cleanup()
    return None

def input(channel):
    global _direction
    global _gpiomode
    global _pintogpio

    if _gpiomode == BOARD:
        channel = _pintogpio[REV][channel]

    return _read_state(channel)

def output(channel, mode):
    global _direction
    global _gpiomode
    global _pintogpio

    if _gpiomode == BOARD:
        channel = _pintogpio[REV][channel]

    if _direction[channel] is not OUT:
        raise Exception('NotAnOutputException')
    else:
        _write_state(channel, mode)
    return None

def set_low_event(channel):
    return None

def set_high_event(channel):
    return None

def set_rising_event(channel):
    return None

def set_falling_event(channel):
    return None

def setwarnings(mode):
    return None

def add_event_detect(gpio, edge, callback, bouncetime = 0):
    if _gpiomode == BOARD:
        channel = _pintogpio[REV][gpio]
    else:
        channel = gpio

    if _direction[channel] is not IN:
        raise RuntimeError("You must setup() the GPIO channel as an input first")

    # TODO: check is it already running and throw an exception
    # RuntimeError("Conflicting edge detection already enabled for this GPIO channel")

def remove_event_detect(channel):
    pass

def event_detected(gpio):
    if _gpiomode == BOARD:
        channel = _pintogpio[REV][gpio]
    else:
        channel = gpio

    # TODO: return value according to the event
    return False

def add_event_callback(gpio, callback):
    if _gpiomode == BOARD:
        channel = _pintogpio[REV][gpio]
    else:
        channel = gpio

    if _direction[channel] is not IN:
        raise RuntimeError("You must setup() the GPIO channel as an input first")
    
    # TODO: if (!gpio_event_added(gpio))
    # raise RuntimeError("Add event detection using add_event_detect first before adding a callback")


def wait_for_edge(channel, edge, bouncetime=0):
    if _gpiomode == BOARD:
        channel = _pintogpio[REV][channel]

    if _direction[channel] is not IN:
        raise RuntimeError("You must setup() the GPIO channel as an input first")

    if edge not in (RISING, FALLING, BOTH):
        raise ValueError("The edge must be set to RISING, FALLING or BOTH")

    # TODO: check if (bouncetime <= 0 && bouncetime != -666)
    # ValueError("Bouncetime must be greater than 0")

    #TODO: check the edge
    # RuntimeError("Conflicting edge detection events already exist for this GPIO channel")

def gpio_function(gpio):
    # TODO mpa pins according to the board type
    return UNKNOWN

class PWM:
    def __init__(self, channel, freq):
        global _gpiomode
        global _pintogpio

        if _gpiomode == BOARD:
            channel = _pintogpio[REV][channel]

        if _direction[channel] is not OUT:
            raise RuntimeError("You must setup() the GPIO channel as an output first")

        if freq <= 0.0:
            raise ValueError("frequency must be greater than 0.0")

    def ChangeDutyCycle(self, dutycycle):
        if dutycycle < 0.0 or dutycycle > 100.0:
            raise ValueError("dutycycle must have a value from 0.0 to 100.0")

    def ChangeFrequency(self, freq):
        if freq <= 0.0:
            raise ValueError("frequency must be greater than 0.0")

    def start(self, dutycycle):
        if (dutycycle < 0.0 or dutycycle > 100.0):
            raise ValueError("dutycycle must have a value from 0.0 to 100.0")

    def stop(self):
        pass

