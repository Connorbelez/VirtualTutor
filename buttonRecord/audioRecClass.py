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
import pyaudio




from deepspeech import Model 
import wave




def tts(stream):
    model = Model('deepspeech-0.9.3-models.tflite')
    model.enableExternalScorer('deepspeech-0.9.3-models.scorer')
    lm_alpha = 0.75
    lm_beta = 1.85
    model.setScorerAlphaBeta(lm_alpha, lm_beta)

    beam_width = 300
    model.setBeamWidth(beam_width)

    # filename = 't2.wav'
    # w = wave.open(filename, 'r')
    # # rate = w.getframerate()
    # frames = w.getnframes()
    # buffer = w.readframes(frames)
    # print(rate)
    import time

    start = time.time()

    print(23*2.3)


    # data16 = np.frombuffer(buffer, dtype=np.int16)

    # pipe_name = "./audioPipe"
    # pipe_fd = os.open(pipe_name, os.O_RDONLY)

    # audio_data = os.read(pipe_fd, 1024)
    # print("Received message:", audio_data)


    # audio_array = np.frombuffer(audio_data, dtype=np.int16)
    print("Getting text...")
    text = model.stt(stream)
    print(text)
    end = time.time()
    print(end - start)
    
    
class audioRecorder:
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    RATE = 16000
    
    def __init__(self, pipeName='/button',model='deepspeech-0.9.3-models.tflite',scorer='deepspeech-0.9.3-models.scorer',channels=1,a=0.75,b=1.85,beam=300 ):
        self.p = pyaudio.PyAudio()
        self.model = Model(model)
        self.model.enableExternalScorer(scorer)
        self.model.setScorerAlphaBeta(a,b)
        self.model.setBeamWidth(beam)
        self.pipeName = pipeName
        self.frames = []
        self.CHANNELS = channels
        
    def sst(self,pipe_name,pupPipe):


        pipe_fd = os.open(pipe_name, os.O_RDONLY)
        # code = code.strip("b").strip('')            
        # code = str(os.read(pipe_fd,1024))

        
        while True:
            print("Listening for button push")
            code = str(os.read(pipe_fd,1024))
            # stream = self.p.open(format=FORMAT,
            # channels=CHANNELS,
            # rate=RATE,
            # input=True,
            # frames_per_buffer=CHUNK)
            
            # stream_context = model.createStream()
            if "P" in code:
                print("Button pushed setting up stream")          
                stream = self.p.open(format=self.FORMAT,
                    channels=self.CHANNELS,
                    rate=self.RATE,
                    input=True,
                    frames_per_buffer=self.CHUNK)
                    
                stream_context = self.model.createStream()
                
                print("CODE: ",code)
                while True:
                    

                    data = stream.read(self.CHUNK)
                    stream_context.feedAudioContent(numpy.frombuffer(data,numpy.int16))
                    
                    if pipe_fd:
                        r, w, e = select.select([pipe_fd], [], [],0)
                        if pipe_fd in r:
                            l = str(os.read(pipe_fd,1024))
                            l = l.strip("b").strip("'")
                            print("118 l: ",l)
                            if l == "R":
                                print("Recording Finished: ")
                                
                                text = stream_context.finishStream()
                                print(text)
                                
                                #now to publish
                                #publish name of file and instructions.
                                break

            else:
                print("Waiting on button")
                    

# class audioRecorder:
#     def __init__(self):
        
#         self.breakFlag = False
#         self.q = queue.Queue()
        

        
#     def int_or_str(self,text):
#         try:
#             return int(text)
#         except ValueError:
#             return text
        
    
#     def callback(self,indata,frames,time,status):
#         """This is called (from a separate thread) for each audio block."""
#         if status:
#             print(status, file=sys.stderr)
#         self.q.put(indata.copy())

#     def initialize(self,pipe_name=None,pubTopic=None):
#         parser = argparse.ArgumentParser(add_help=False)
#         parser.add_argument(
#             '-l', '--list-devices', action='store_true',
#             help='show list of audio devices and exit')
        
#         args, remaining = parser.parse_known_args()
#         # q = queue.Queue()

#         if args.list_devices:
#             print(sd.query_devices())
#             parser.exit(0)
#         parser = argparse.ArgumentParser(
#             description=__doc__,
#             formatter_class=argparse.RawDescriptionHelpFormatter,
#             parents=[parser])
#         parser.add_argument(
#             'filename', nargs='?', metavar='FILENAME',
#             help='audio file to store recording to')
#         parser.add_argument(
#             '-d', '--device', type=self.int_or_str,
#             help='input device (numeric ID or substring)')
#         parser.add_argument(
#             '-r', '--samplerate', type=int, help='sampling rate')
#         parser.add_argument(
#             '-c', '--channels', type=int, default=1, help='number of input channels')
#         parser.add_argument(
#             '-t', '--subtype', type=str, help='sound file subtype (e.g. "PCM_24")')
#         args = parser.parse_args(remaining)
        

        
#         pipe_fd = os.open(pipe_name, os.O_RDONLY)
    
        
#         while True:
    
#             if args.samplerate is None:
#                 device_info = sd.query_devices(args.device, 'input')
#                 # soundfile expects an int, sounddevice provides a float:
#                 # args.samplerate = int(device_info['default_samplerate'])
#                 args.samplerate = 16000
#             # if args.filename is None:
#             #     args.filename = tempfile.mktemp(prefix='delme_rec_unlimited_',
#             #                                     suffix='.wav', dir='')

#             # Make sure the file is opened before recording anything:
#             code = str(os.read(pipe_fd,1024))
#             print(code)
#             code = code.strip("b").strip("'")
#             self.q.queue.clear()
#             if "P" in code:
#                 print("Starting Recording...")
#                 # args.filename = tempfile.mktemp(prefix='delme_rec_unlimited_',
#                 #                                     suffix='.wav', dir='')
#                 if os.path.exists("t2.wav"):
#                     os.remove("t2.wav")
#                 args.filename = "t2.wav"
#                 with sf.SoundFile(args.filename, mode='x', samplerate=args.samplerate,
#                                 channels=args.channels, subtype=args.subtype) as file:
#                     with sd.InputStream(samplerate=args.samplerate, device=args.device,
#                                         channels=args.channels, callback=self.callback):
#                         print('#' * 80)
#                         print('press Ctrl+C to stop the recording')
#                         print('#' * 80)
#                         audioBuffer = []
#                         while True:
#                             if pipe_fd:
#                                 r, w, e = select.select([pipe_fd], [], [],0)
#                                 if pipe_fd in r:
#                                     l = str(os.read(pipe_fd,1024))
#                                     l = l.strip("b").strip("'")
#                                     print(l)
#                                     if l == "R":
#                                         print("Recording Finished: ",repr(args.filename))
                                        
                                        
#                                         #publish name of file and instructions.
#                                         break
#                                 # message = os.read(pipe_fd, 1024)
#                                 # print("MESSAGE FROM AR: ",message)
#                             tw = self.q.get()
#                             print("tw Len: ",len(audioBuffer))
#                             # file.write(self.q.get())
#                             audioBuffer.append(tw)
#                             file.write(tw)
#                             print("Writing: ",tw)

                
#                         if pubTopic:
#                             print("opening Publish Pipe")
#                             print(type(audioBuffer))
#                             pub_topic_fd = os.open(pubTopic, os.O_WRONLY | os.O_NONBLOCK) #if theres an error here its because there's no listener attached to it yet. 
#                             # pub_topic_fd = open(pubTopic,"wb")
#                             print("Opened Pub Pipe")
#                             # message = bytes(str(audioBuffer),encoding='utf-8')
#                             ab = b''.join(audioBuffer)
#                             audio_array = numpy.frombuffer(ab, dtype=numpy.int16)
                            
                        
#                             print("MEssge: ",ab)
#                             # message = audioBuffer
#                             # os.write(pub_topic_fd, message)
#                             os.write(pub_topic_fd, ab)
#                             print(len(ab))
#                             tts(audio_array)
#                             # pub_topic_fd.write()
#                             # print("PUBLISHED FILE NAME: ",message)
#         # except KeyboardInterrupt:
#         #     print('\nRecording finished: ' + repr(args.filename))
#         #     parser.exit(0)
#         # except Exception as e:
#         #     parser.exit(type(e).__name__ + ': ' + str(e))
            
    