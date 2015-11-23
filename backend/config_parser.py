import json
import os

class Struct(object):

    def __init__(self, data):
        for name, value in data.iteritems():
            setattr(self, name, self._wrap(value))

    def _wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)): 
            return type(value)([self._wrap(v) for v in value])
        else:
            return Struct(value) if isinstance(value, dict) else value

config_dir = os.path.abspath(os.path.dirname(__file__))
config_path = os.path.join(config_dir, "chronos_config.json")

with open(config_path) as config:
    cfg = json.load(config, object_hook=Struct)