import pyaudio
import wave
import audioop
from collections import deque 
import os
import time

def find_input_device(pyaudio):
        device_index = None            
        for i in range( pyaudio.get_device_count() ):     
            devinfo = pyaudio.get_device_info_by_index(i)   
            print( "Device %d: %s"%(i,devinfo["name"]) )

            for keyword in ["mic","input"]:
                if keyword in devinfo["name"].lower():
                    print( "Found an input: device %d - %s"%(i,devinfo["name"]) )
                    device_index = i
                    return device_index

        if device_index == None:
            print( "No preferred input found; using default input device." )

        return device_index

def listen_for_block_of_speech():

    #config
    chunk = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    THRESHOLD = 180 #The threshold intensity that defines silence signal (lower than).
    SILENCE_LIMIT = 2 #Silence limit in seconds. The max ammount of seconds where only silence is recorded. When this time passes the recording finishes and the file is delivered.

    #open stream
    p = pyaudio.PyAudio()

    stream = p.open(format = FORMAT,
                    channels = CHANNELS,
                    rate = RATE,
                    input = True,
                    input_device_index = find_input_device(p),
                    frames_per_buffer = chunk)

    all_m = []
    data = ''
    SILENCE_LIMIT = 2
    rel = RATE/chunk
    slid_win = deque(maxlen=SILENCE_LIMIT*rel)
    started = False
    finished = False
    
    while (not finished):
        data = stream.read(chunk)
        slid_win.append (abs(audioop.avg(data, 2)))
        if(True in [ x>THRESHOLD for x in slid_win]):
            if(not started):
                print("starting to record")
            started = True
            all_m.append(data)
        elif (started==True):
            wav_filename = save_speech(all_m,p)
            flac_filename = convert_wav_to_flac(wav_filename)
            #reset all
            started = False
            finished = True
        else:
            all_m = []
            all_m.append(data)

    stream.close()
    p.terminate()
    return flac_filename

def save_speech(data, p):
    filename = 'output_'+str(int(time.time()))
    # write data to WAVE file
    data = ''.join(data)
    wf = wave.open(filename+'.wav', 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(16000)
    wf.writeframes(data)
    wf.close()
    return filename

def convert_wav_to_flac(filename):
	os.system(FLAC_CONV+ filename+'.wav')
	os.remove(filename+'.wav')
	flac_filename = filename+'.flac'
	return flac_filename


FLAC_CONV = 'flac -f ' # We need a WAV to FLAC converter.
if(__name__ == '__main__'):
    # Unit test when module is run
    filename = listen_for_block_of_speech()
    os.system('mplayer ' + filename)
    os.remove(filename)