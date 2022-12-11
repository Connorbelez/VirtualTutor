import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import time

import argparse
import tempfile
import queue
import sys
import os
import sounddevice as sd
import soundfile as sf
import numpy  # Make sure NumPy is loaded before it is used in the callback
assert numpy  # avoid "imported but unused" message (W0611)

class testClass:
    def __init__(self):
        self.bFlag = False
    
    
    def loop(self,pipe_fd=None):
        buttonPressed = False
        buttonReleased = False
        while True:
            if self.bFlag:
                self.bFlag = False
                break
            time.sleep(0.1)
            if pipe_fd:
                message = os.read(pipe_fd, 1024)
                print("MSG REC!: ",message)
                buttonPressed = True
            
            if buttonPressed:
                print("BUTTON HELD!!!")
                
            if buttonPressed and buttonReleased:
                print("Button Released")
                break
        print("LOOP BROKEn")
        
            
        



class audioRecorder:
    def __init__(self):
        
        self.breakFlag = False
        
        self.parser = argparse.ArgumentParser(add_help=False)
        self.parser.add_argument(
            '-l', '--list-devices', action='store_true',
            help='show list of audio devices and exit')
        
        self.args, self.remaining = parser.parse_known_args()
        
        if self.args.list_devices:
            print(sd.query_devices())
            parser.exit(0)
        self.parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            parents=[parser])
        self.parser.add_argument(
            'filename', nargs='?', metavar='FILENAME',
            help='audio file to store recording to')
        self.parser.add_argument(
            '-d', '--device', type=int_or_str,
            help='input device (numeric ID or substring)')
        self.parser.add_argument(
            '-r', '--samplerate', type=int, help='sampling rate')
        self.parser.add_argument(
            '-c', '--channels', type=int, default=1, help='number of input channels')
        self.parser.add_argument(
            '-t', '--subtype', type=str, help='sound file subtype (e.g. "PCM_24")')
        self.args = self.parser.parse_args(remaining)
        
        self.q = queue.Queue()
        
    def callback(self,indata,frames,time,status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        q.put(indata.copy())

    def beginRecording(self,pipe_fd=None):
        
        try:
            if args.samplerate is None:
                device_info = sd.query_devices(args.device, 'input')
                # soundfile expects an int, sounddevice provides a float:
                args.samplerate = int(device_info['default_samplerate'])
            if args.filename is None:
                args.filename = tempfile.mktemp(prefix='delme_rec_unlimited_',
                                                suffix='.wav', dir='')

            # Make sure the file is opened before recording anything:
            with sf.SoundFile(args.filename, mode='x', samplerate=args.samplerate,
                            channels=args.channels, subtype=args.subtype) as file:
                with sd.InputStream(samplerate=args.samplerate, device=args.device,
                                    channels=args.channels, callback=callback):
                    print('#' * 80)
                    print('press Ctrl+C to stop the recording')
                    print('#' * 80)
                    while True:
                        if pipe_fd:
                            message = os.read(pipe_fd, 1024)
                            print("MESSAGE FROM AR: ",message)
                        file.write(q.get())
        except KeyboardInterrupt:
            print('\nRecording finished: ' + repr(args.filename))
            parser.exit(0)
        except Exception as e:
            parser.exit(type(e).__name__ + ': ' + str(e))
            
    
# GPIO.setwarnings(False) # Ignore warning for now
# GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
# GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)

class Button:
    def __init__(self):
        GPIO.setwarnings(False) # Ignore warning for now
        GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
        GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)
        self.bps = 0
        self.button = 0
        self.terminate = 0
    
    def listen(self,outPipe=None):
        
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
                
                if outPipe:
                    message = b"P"
                    os.write(outPipe, message)
                self.bps = 1
            else:
                if outPipe:
                    message = b"R"
                    os.write(outPipe, message)
                    
                
                print("Released")
                self.bps = 0

            
        GPIO.cleanup()
    