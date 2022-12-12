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
import select 
class testClass:
    def __init__(self):
        self.bFlag = False
        # self.pipe_fd = os.open(pipe_name, os.O_RDONLY | os.O_NONBLOCK)
    
    
    def loop(self,pipe_name=None):
        print("IN LOOOP")
        pipe_fd = os.open(pipe_name, os.O_RDONLY | os.O_NONBLOCK)
        print("opened")
        buttonPressed = False
        buttonReleased = False
        print("Entering while ")
        while True:

            if self.bFlag:
                self.bFlag = False
                break
            # time.sleep(0.1)
            # print("select")
            r, w, e = select.select([pipe_fd], [], [],0)
            # print("R: ",r)
            # print('.')
            if pipe_fd in r:
                l = str(os.read(pipe_fd,1024))
                l = l.strip("b").strip("'")
                print(l)
                if l == "R":
                    break
            else:
                # print("No data")
                continue
            
            # print(".")
            # time.sleep(0.5)
            # if pipe_fd:
                
            #     message = os.read(pipe_fd, 1024)
            #     print("message: ",message)
            
                
            print(".")
            # if buttonPressed:
            #     print("BUTTON HELD!!!")
                
            # if buttonPressed and buttonReleased:
            #     print("Button Released")
            #     break
        print("LOOP BROKEn")
        
            
        

class audioRecorder:
    def __init__(self):
        
        self.breakFlag = False
        self.q = queue.Queue()
        

        
    def int_or_str(self,text):
        try:
            return int(text)
        except ValueError:
            return text
        
    
    def callback(self,indata,frames,time,status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        self.q.put(indata.copy())

    def initialize(self,pipe_name=None,pubTopic=None):
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument(
            '-l', '--list-devices', action='store_true',
            help='show list of audio devices and exit')
        
        args, remaining = parser.parse_known_args()
        # q = queue.Queue()

        if args.list_devices:
            print(sd.query_devices())
            parser.exit(0)
        parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            parents=[parser])
        parser.add_argument(
            'filename', nargs='?', metavar='FILENAME',
            help='audio file to store recording to')
        parser.add_argument(
            '-d', '--device', type=self.int_or_str,
            help='input device (numeric ID or substring)')
        parser.add_argument(
            '-r', '--samplerate', type=int, help='sampling rate')
        parser.add_argument(
            '-c', '--channels', type=int, default=1, help='number of input channels')
        parser.add_argument(
            '-t', '--subtype', type=str, help='sound file subtype (e.g. "PCM_24")')
        args = parser.parse_args(remaining)
        

        
        pipe_fd = os.open(pipe_name, os.O_RDONLY)
    
        
        while True:
    
            if args.samplerate is None:
                device_info = sd.query_devices(args.device, 'input')
                # soundfile expects an int, sounddevice provides a float:
                args.samplerate = int(device_info['default_samplerate'])
            # if args.filename is None:
            #     args.filename = tempfile.mktemp(prefix='delme_rec_unlimited_',
            #                                     suffix='.wav', dir='')

            # Make sure the file is opened before recording anything:
            code = str(os.read(pipe_fd,1024))
            print(code)
            code = code.strip("b").strip("'")
            self.q.queue.clear()
            if "P" in code:
                print("Starting Recording...")
                args.filename = tempfile.mktemp(prefix='delme_rec_unlimited_',
                                                    suffix='.wav', dir='')
            
                with sf.SoundFile(args.filename, mode='x', samplerate=args.samplerate,
                                channels=args.channels, subtype=args.subtype) as file:
                    with sd.InputStream(samplerate=args.samplerate, device=args.device,
                                        channels=args.channels, callback=self.callback):
                        print('#' * 80)
                        print('press Ctrl+C to stop the recording')
                        print('#' * 80)
                        while True:
                            if pipe_fd:
                                r, w, e = select.select([pipe_fd], [], [],0)
                                if pipe_fd in r:
                                    l = str(os.read(pipe_fd,1024))
                                    l = l.strip("b").strip("'")
                                    print(l)
                                    if l == "R":
                                        print("Recording Finished: ",repr(args.filename))
                                        
                                        
                                        #publish name of file and instructions.
                                        break
                                # message = os.read(pipe_fd, 1024)
                                # print("MESSAGE FROM AR: ",message)
                            file.write(self.q.get())
                        if pubTopic:
                            print("opening Publish Pipe")
                            pub_topic_fd = os.open(pubTopic, os.O_WRONLY | os.O_NONBLOCK) #if theres an error here its because there's no listener attached to it yet. 
                            print("Opened Pub Pipe")
                            message = bytes(str(args.filename),encoding='utf-8')
                            os.write(pub_topic_fd, message)
                            print("PUBLISHED FILE NAME: ",message)
        # except KeyboardInterrupt:
        #     print('\nRecording finished: ' + repr(args.filename))
        #     parser.exit(0)
        # except Exception as e:
        #     parser.exit(type(e).__name__ + ': ' + str(e))
            
    
class Button:
    def __init__(self):
        GPIO.setwarnings(False) # Ignore warning for now
        GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
        GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)
        self.bps = 0
        self.button = 0
        self.terminate = 0
        
    
    def listen(self,pipe_fd=None):
        print("LISTENING at :", pipe_fd)
        outPipe = os.open(pipe_fd, os.O_WRONLY)
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
    