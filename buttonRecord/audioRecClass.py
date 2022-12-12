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
            
    