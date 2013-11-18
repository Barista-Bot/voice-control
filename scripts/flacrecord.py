import pyaudio
import wave
import audioop
from collections import deque
from googletext2speech import play_wav
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

def calibrate_input_threshold(audioStream, chunk):
	print "Calibrating audio stream threshold"
	currentMaximum = 0
	for i in range(1,10):
		data = audioStream.read(chunk)
        soundLevel = abs(audioop.avg(data, 2))
        if soundLevel > currentMaximum:
        	currentMaximum = soundLevel
	if currentMaximum < 100:
		currentMaximum += 100
	print "Setting calibration level to " + str(currentMaximum)
	return currentMaximum


def listen_for_block_of_speech():

    #config
    chunk = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    PRE_SAMPLES = 10
    SILENCE_LIMIT = 1 #Silence limit in seconds. The max ammount of seconds where only silence is recorded. When this time passes the recording finishes and the file is delivered.

    #open stream
    p = pyaudio.PyAudio()

    stream = p.open(format = FORMAT,
                    channels = CHANNELS,
                    rate = RATE,
                    input = True,
                    input_device_index = find_input_device(p),
                    frames_per_buffer = chunk)

    THRESHOLD = calibrate_input_threshold(stream, chunk)

    all_m = []
    data = ''
    SILENCE_LIMIT = 2
    rel = RATE/chunk
    slid_win = deque(maxlen=SILENCE_LIMIT*rel)
    started = False
    finished = False

    play_wav(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'raw/soundstart.wav'))
    
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
			if len(all_m) > PRE_SAMPLES:
				all_m.pop(0)
			all_m.append(data)

    play_wav(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'raw/soundstop.wav'))

    stream.close()
    p.terminate()
    return flac_filename

def save_speech(data, p):
    filename = os.path.join(os.path.dirname(os.path.realpath(__file__)),'output_'+str(int(time.time())))
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