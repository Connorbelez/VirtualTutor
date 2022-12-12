from myLib import Button, testClass
from audioRecClass import audioRecorder
import threading
import sys
import os

import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import time

# pipe_name = "./button"
# pub_topic = "./fileNameTopic"

pipes = ["./button", "./fileNameTopic"]
pipes = [os.path.abspath(pip) for pip in pipes]

for pipe in pipes:
    if not os.path.exists(pipe):
        os.mkfifo(pipe, 0o666)
    # else:
    #     os.remove(pipe)
    #     os.mkfifo(pipe, 0o666)
        


b = Button()
r = audioRecorder()
t1 = threading.Thread(target=b.listen, args=(pipes[0],))
t2 = threading.Thread(target=r.initialize, args=(pipes[0],pipes[1]))

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