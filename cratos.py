
# %%
from ppadb.client import Client
import cv2
import numpy as np
from numpy import random
from datetime import datetime
import time
import requests
import os
from appteck_function import *

device, client = connect()


# %%
device.input_keyevent('KEYCODE_SLEEP')
# %%
device.input_keyevent('KEYCODE_WAKEUP')

# %%
device.input_keyevent('KEYCODE_HOME')

#%%
save_cap('example_home')

