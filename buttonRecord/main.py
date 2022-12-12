from myLib import Button, testClass
from audioRecClass import audioRecorder
import threading
import sys
import os

import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import time

pipe_name = "./button"


if not os.path.exists(pipe_name):
    os.mkfifo(pipe_name, 0o666)
else:
    os.remove(pipe_name)
    os.mkfifo(pipe_name, 0o666)
b = Button()
r = audioRecorder()
t1 = threading.Thread(target=b.listen, args=(pipe_name,))
t2 = threading.Thread(target=r.initialize, args=(pipe_name,))

t2.start()
t1.start()
# b.listen(pipe_name)
# print("entering whileLoop")
# while True:
#     message = os.read(pipe_fd, 1024)
#     print("Received messageasdf:", message)
# # b.listen(outpipe_fd)
# t1.start()
# # t2.start()

# t1.join()

# r = audioRecorder()

# r.beginRecording(pipe_fd)