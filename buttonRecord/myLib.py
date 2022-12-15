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
import requests



from deepspeech import Model 
import wave


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
            if pipe_fd in r:
                l = str(os.read(pipe_fd,1024))
                l = l.strip("b").strip("'")
                print(l)
                if l == "R":
                    break
            else:
                # print("No data")
                continue

            print(".")

        print("LOOP BROKEn")
        
 
    
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
from gtts import gTTS
import openai
class OpenAiClient:
    def __init__(self):
        self.url = "https://api.openai.com/v1/models/davinci-3"
        self.api_key = os.environ.get("OPENAIKEY")
        self.conversation_id = "a;lsdkfj123";
        self.max_tokens = 500
        self.temperature = 0.5
        self.response_type = 'text'
        self.context = []
        self.gradeLevel = "University"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
            }

        
    def req(self,text):
        text = str(text)
        print("NEW PROMPT: ",text)
        openai.api_key = os.getenv("OPENAIKEY")
        
        self.context.append("Student: " + text + "\n" + "Teacher: ")
        
        prompt = " ".join(self.context)
        c = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=200,
            temperature=0
        )
        response = c["choices"][0]["text"].strip()
        if len(self.context) <1:
            
            self.context.append("Teacher: " + response + "\n")
        else:
            self.context.append("Teacher: " + response + "\n")
        print("RESPONSE FROM OPEN AI: ",response)
        print(self.context)

        myobj = gTTS(text=response, lang='en', slow=False)
        
        # Saving the converted audio in a mp3 file named
        # welcome 
        myobj.save("welcome.mp3")
        
        # Playing the converted file
        os.system("mpg321 welcome.mp3")
        # # self.data["prompt"] = text
        # print("Making request with text: ",text)
        # response = requests.post("https://api.openai.com/v1/completions", headers=self.headers, json=c)
        # print(response.text)
        
    def listen(self,pipe):
        pipe_fd = os.open(pipe, os.O_RDONLY)
        self.context.append("You are a teacher, answering the questions of a " + self.gradeLevel + " level student\n")
        while True:

            audio_data = os.read(pipe_fd, 1024)
            print("Received message:", audio_data)
            text = str(audio_data)
            print(text)
            self.req(text)


# Set the URL for the Davinci-3 model
# url = "https://api.openai.com/v1/models/davinci-3"

# # Set the API key
# api_key = "<your-api-key>"

# # Set the conversation ID
# conversation_id = "<your-conversation-id>"

# # Set the prompt text that you want to generate a response for
# prompt = "What is the weather like today?"

# # Set the maximum number of characters that the response can contain
# max_tokens = 100

# # Set the temperature parameter (controls the creativity of the response)
# temperature = 0.5

# # Set the response type to "text"
# response_type = "text"

# # Set the request headers
# headers = {
#   "Content-Type": "application/json",
#   "Authorization": f"Bearer {api_key}"
# }

# # Set the request body
# data = {
#   "prompt": prompt,
#   "max_tokens": max_tokens,
#   "temperature": temperature,
#   "response_format": response_type,
#   "conversation_id": conversation_id
# }

# Make the request to the Davinci-3 model
# response = requests.post(url, headers=headers, json=data)

# # Print the response
# print(response.text)
