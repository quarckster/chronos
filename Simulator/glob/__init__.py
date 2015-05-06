# 1. create a dirs /tmp/w1/device1 and /tmp/w1/device2
# 2. create file in /tmp/w1/device1/name and put string 28-00042d4367ff into it
# 3. create file in /tmp/w1/device1/w1_slave
# it should contain the next lines:
# YES
# t=2000.0
# 4.create file in /tmp/w1/device2/name and put string 28-00042c648eff into it
# 5. create file in /tmp/w1/device2/w1_slave
# it should contain the same lines (the same format) as in p.3

_DEFAULT_PATH = '/tmp/w1/device'


def glob(base_dir):
    # it always returns list of path(s)
    path = [_DEFAULT_PATH + '1', _DEFAULT_PATH + '2']

    return path
