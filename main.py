from myLib import Button, testClass, OClient
from audioRecClass import audioRecorder
import threading
import sys
import os

import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import time
import pyaudio
import openai

pipes = ["./button", "./audioPipe"]
pipes = [os.path.abspath(pip) for pip in pipes]

for pipe in pipes:
    if not os.path.exists(pipe):
        os.mkfifo(pipe, 0o666)
    # else:
    #     os.remove(pipe)
    #     os.mkfifo(pipe, 0o666)
        

c = OClient()
b = Button()
r = audioRecorder()
t3 = threading.Thread(target=c.listen, args=(pipes[1],))
t1 = threading.Thread(target=b.listen, args=(pipes[0],))
t2 = threading.Thread(target=r.sst, args=(pipes[0],pipes[1]))

t3.start()
t2.start()
t1.start()



