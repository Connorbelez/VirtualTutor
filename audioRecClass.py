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

    import time

    start = time.time()

    print(23*2.3)
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
        
    def sst(self,pipe_name,pubPipe):


        pipe_fd = os.open(pipe_name, os.O_RDONLY)

        pubTopic = os.open(pubPipe, os.O_WRONLY)
        
        while True:
            print("Listening for button push")
            code = str(os.read(pipe_fd,1024))

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
                                os.write(pubTopic,bytes(text,encoding='utf-8'))
                                #publish name of file and instructions.
                                break

            else:
                print("Waiting on button")
 