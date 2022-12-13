# deepspeech --model deepspeech-0.9.3-models.tflite --scorer deepspeech-0.9.3-models.scorer --audio audio/2830-3980-0043.wav
# deepspeech --model deepspeech-0.9.3-models.tflite --scorer deepspeech-0.9.3-models.scorer --audio audio/4507-16021-0012.wav
# deepspeech --model deepspeech-0.9.3-models.tflite --scorer deepspeech-0.9.3-models.scorer --audio audio/8455-210777-0068.wav




# --scorer deepspeech-0.9.3-models.scorer
import soundfile as sf
from deepspeech import Model 
import wave
import numpy as np
import os





def readText():
        # Open the named pipe for reading
    
    pipe_name = "./audioPipe"
    pipe_fd = os.open(pipe_name, os.O_RDONLY)

    audio_data = os.read(pipe_fd, 1024)
    print("Received message:", audio_data)


    audio_array = np.frombuffer(audio_data, dtype=np.int16)

    # wave_file = wave.open('my_audio_file.wav', 'wb')

    # # Set the wave file parameters
    # num_channels = 1  # mono
    # sample_width = 2  # 16-bit
    # sample_rate = 16000
    # num_frames = len(audio_array)
    # comptype = 'NONE'
    # compname = 'not compressed'

    # # Set the wave file parameters and write the header
    # wave_file.setparams((num_channels, sample_width, sample_rate,
    #                     num_frames, comptype, compname))

    # # Write the audio data to the wave file
    # wave_file.writeframes(audio_array)
    print("FIle Written")
# # Close the named pipe
    # os.close(pipe_fd)

# readText()


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

pipe_name = "./audioPipe"
pipe_fd = os.open(pipe_name, os.O_RDONLY)

audio_data = os.read(pipe_fd, 1024)
print("Received message:", audio_data)


audio_array = np.frombuffer(audio_data, dtype=np.int16)
print("Getting text...")
text = model.stt(audio_array)
print(text)
end = time.time()
print(end - start)