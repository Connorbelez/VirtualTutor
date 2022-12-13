from deepspeech import Model 
import wave
import numpy as np

class ASR:
    def __init__(self,a=0.75,b=1.85,beam=300):
        self.model = Model('deepspeech-0.9.3-models.tflite')
        self.model.enableExternalScorer('deepspeech-0.9.3-models.scorer')
        self.lm_alpha = a
        self.lm_beta = b
        self.model.setBeamWidth(beam)
    
    def stt(self,filename):
        
        
        
        