from myLib import Button, audioRecorder, testClass
import threading
import sys
import os

import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import time

pipe_name = "./button"
import threading

# Open the named pipe for writing
# if  os.path.exists(pipe_name):
#     pipe_fd = os.open(pipe_name, os.O_WRONLY)
#     os.close()

if not os.path.exists(pipe_name):
    os.mkfifo(pipe_name, 0o666)
    
outpipe_fd = os.open(pipe_name, os.O_WRONLY)
inPipe_fd = os.open(pipe_name, os.O_RDONLY | os.O_NONBLOCK)
nessage = b"testtestetesrt"
os.write(outpipe_fd,nessage)

b = Button()

t1 = threading.Thread(target=b.listen(outpipe_fd))
t2 = 
# b.listen(outpipe_fd)

t1.start()

# r = audioRecorder()

# r.beginRecording(pipe_fd)