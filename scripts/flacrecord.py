import pyaudio
import wave
import audioop
from collections import deque
from googletext2speech import play_wav
import os
import time
import globalvariables
from globalvariables import *


def find_input_device(pyaudio):
        device_index = None            
        for i in range( pyaudio.get_device_count() ):     
            devinfo = pyaudio.get_device_info_by_index(i)   
            print( "Device %d: %s"%(i,devinfo["name"]) )

            for keyword in []:
                if keyword in devinfo["name"].lower():
                    print( "Found an input: device %d - %s"%(i,devinfo["name"]) )
                    device_index = i
                    return device_index

        if device_index == None:
            print( "-----------No preferred input found; using default input device.-----------" )

        return device_index

def calibrate_input_threshold():
	#open stream
	p = pyaudio.PyAudio()

	print "-----------Calibrating audio stream threshold-----------"
	noise = 0
	noiseTotal = 0
	try:
		stream = p.open(format = FORMAT, channels = CHANNELS, rate = SAMPLERATE, input = True, input_device_index = find_input_device(p), frames_per_buffer = CHUNK)
	except IOError, e:
		if e.args[1] == pyaudio.paInvalidSampleRate:
			globalvariables.SAMPLERATE = 44100
			stream = p.open(format = FORMAT, channels = CHANNELS, rate = SAMPLERATE, input = True, input_device_index = find_input_device(p), frames_per_buffer = CHUNK)
		else:
			raise

	for i in range(CALIBRATION_RANGE):
		data = stream.read(CHUNK)
		noiseTotal += abs(audioop.avg(data, 2))

	stream.close()
	p.terminate()
	
	noise = (noiseTotal / CALIBRATION_RANGE)
	noise *= THRESHOLD_AMPLIFICATION
	print "-----------Setting calibration level to " + str(noise) + "-----------"
	global THRESHOLD
	THRESHOLD = noise
	

def cancel_interaction():
	global finished
	finished = True

def averageLevel(sliding_window):
	noise = 0
	for sample in sliding_window:
		noise += sample

	return (noise / len(sliding_window))

def listen_for_block_of_speech():

	calibrate_input_threshold()

	#config
	global THRESHOLD
	#THRESHOLD = 50

	#open stream
	p = pyaudio.PyAudio()

	all_m = []
	data = ''
	SILENCE_LIMIT = 2
	rel = SAMPLERATE/CHUNK
	slid_win = deque(maxlen=(SILENCE_LIMIT*rel))
	started = False
	global finished
	finished = False

	play_wav(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'raw/soundstart.wav'))
	
	time.sleep(0.2)

	try:
		stream = p.open(format = FORMAT, channels = CHANNELS, rate = SAMPLERATE, input = True, input_device_index = find_input_device(p), frames_per_buffer = CHUNK)
	except IOError, e:
		if e.args[1] == pyaudio.paInvalidSampleRate:
			globalvariables.SAMPLERATE = 44100
			stream = p.open(format = FORMAT, channels = CHANNELS, rate = SAMPLERATE, input = True, input_device_index = find_input_device(p), frames_per_buffer = CHUNK)
		else:
			raise
	globalvariables.PRE_SAMPLES=0.5*rel
	startTime = time.time()

	while (not finished):
		try:
			data = stream.read(CHUNK)
			currTime = time.time()
		except IOError, e:
			if e.args[1] == pyaudio.paInputOverflowed:
				data = '\x00'*CHUNK
			else:
				raise
		slid_win.append(abs(audioop.avg(data, 2)))
		average = averageLevel(slid_win)
		print "Average of window: " + str(average) + " threshold: " + str(THRESHOLD)
		print "Time Elapsed: " + str(currTime - startTime) 
		if(average > THRESHOLD):
			if(not started):
				print("starting to record")
				started = True
				all_m.append(data)
				startTime = time.time()
			else:
				all_m.append(data)
				if(currTime - startTime > 15):
					print "-----------Stopped recording due to timeout-----------"
					wav_filename = save_speech(all_m,p)
					flac_filename = convert_wav_to_flac(wav_filename)
					started = False
					finished = True
		elif (started==True):
			print "-----------Stopped recording-----------"
			wav_filename = save_speech(all_m,p)
			flac_filename = convert_wav_to_flac(wav_filename)
			started = False
			finished = True
		else:
			if len(all_m) > PRE_SAMPLES:
				all_m.pop(0)
			all_m.append(data)
			if (not started and (currTime - startTime > 10)):
				print "----------Stopped recording as nothing heard----------"
				finished = True

	stream.close()
	p.terminate()

	play_wav(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'raw/soundstop.wav'))

	if 'flac_filename' in locals():
		return flac_filename
	else:
		return []

def save_speech(data, p):
    filename = os.path.join(os.path.dirname(os.path.realpath(__file__)),'output_'+str(int(time.time())))
    # write data to WAVE file
    data = ''.join(data)
    wf = wave.open(filename+'.wav', 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(SAMPLERATE)
    wf.writeframes(data)
    wf.close()
    return filename

def convert_wav_to_flac(filename):
	os.system(FLAC_CONV + filename+'.wav')
	os.remove(filename+'.wav')
	flac_filename = filename+'.flac'
	return flac_filename


FLAC_CONV = 'flac -f ' # We need a WAV to FLAC converter.
if(__name__ == '__main__'):
    # Unit test when module is run
    filename = listen_for_block_of_speech()
    os.system('mplayer ' + filename)
    os.remove(filename)
