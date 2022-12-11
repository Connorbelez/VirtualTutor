import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import time

# GPIO.setwarnings(False) # Ignore warning for now
# GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
# GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)

import threading
def my_inline_function(some_args):
    # do some stuff
    thread = threading.Thread(target=function_that_downloads, name="Downloader", args=some_args)
    thread.start()
    # continue doing stuff
    
    
class Button:
    def __init__(self):
        GPIO.setwarnings(False) # Ignore warning for now
        GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
        GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)
        self.bps = 0
        self.button = 0
        self.terminate = 0
    
    
    # def threadListendef(s):
    # # do some stuff
    # thread = threading.Thread(target=function_that_downloads, name="Downloader", args=some_args)
    # thread.start()
    def listen(self):
        while True:
            if self.terminate:
                self.terminate = 0
                break
            time.sleep(0.1)
            self.Button = GPIO.input(10)

            if self.Button == self.bps:
                continue
            elif self.Button:
                print("Button was pushed!")
                self.bps = 1
            else:
                print("Released")
                self.bps = 0

            
        GPIO.cleanup()
    

b = Button()
b.listen()