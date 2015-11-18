import logging
import sys
import os
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from chronos import app as application