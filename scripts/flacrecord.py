#!/usr/bin/env python2
import pyaudio
import wave
import audioop
from collections import deque
from googletext2speech import play_wav
import os
import time
import globalvariables
#from globalvariables import *
import rospy
from face.msg import faceRequests

def open_stream():
	global p
	p = pyaudio.PyAudio()
	try:
		stream = p.open(format = globalvariables.FORMAT, channels = globalvariables.CHANNELS, rate = globalvariables.SAMPLERATE, input = True, input_device_index = find_input_device(p), frames_per_buffer = globalvariables.SAMPLES_PER_CHUNK)
	except IOError, e:
		if e.args[1] == pyaudio.paInvalidSampleRate:
			globalvariables.globalvariables.SAMPLERATE = 44100
			stream = p.open(format = globalvariables.FORMAT, channels = globalvariables.CHANNELS, rate = globalvariables.SAMPLERATE, input = True, input_device_index = find_input_device(p), frames_per_buffer = globalvariables.SAMPLES_PER_CHUNK)
		else:
			raise
	return stream

def close_stream(stream):
	global p
	stream.close()
	p.terminate()

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

def calibrate_input_threshold(stream):
	try:
		stream.start_stream()
	except:
		pass
	print "-----------Calibrating audio stream threshold-----------"

	slid_win = deque(maxlen=globalvariables.MAX_SLID_WIN_LEN)

	for i in range(globalvariables.CALIBRATION_RANGE):
		chunk_data = stream.read(globalvariables.SAMPLES_PER_CHUNK)
		chunk_avg = abs(audioop.avg(chunk_data, 2))
		slid_win.append(chunk_avg)
		slid_win_average = averageLevel(slid_win)
		print " Sliding window average:", slid_win_average

	stream.stop_stream()

	global THRESHOLD
	THRESHOLD = slid_win_average
	THRESHOLD *= globalvariables.THRESHOLD_AMPLIFICATION
	print "-----------Setting calibration level to " + str(THRESHOLD) + "-----------"
		

def cancel_interaction():
	global finished
	global interaction_cancelled
	finished = True
	interaction_cancelled = True

def averageLevel(sliding_window):
	noise = 0
	for sample in sliding_window:
		noise += sample

	return (noise / len(sliding_window))

class FaceController(object):
	def __init__(self):
		self.pub = rospy.Publisher('/face/control', faceRequests)

	def update(self, is_talking=False, message=''):
		self.pub.publish(faceRequests(talking=is_talking, question=message))

def listen_for_block_of_speech(stream):

	global interaction_cancelled

	print "THRESHOLD", THRESHOLD

	full_recording = []
	max_recording_chunks = 15 * globalvariables.CHUNKS_PER_SECOND
	slid_win = deque(maxlen=globalvariables.MAX_SLID_WIN_LEN)
	slid_win.extend([0]*globalvariables.MAX_SLID_WIN_LEN)
	recording_started = False
	interaction_cancelled = False
	face_controller = FaceController()
	
	stream.start_stream()
	play_wav(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'raw/soundstart.wav'))
	stream.read(int(globalvariables.SAMPLERATE*0.55))
	
	listening_start_time = time.time()
	face_controller.update(message="Speak now...")
	while True:
		if interaction_cancelled:
			print "-----------Recording cancelled-----------"
			full_recording = []
			break

		try:
			chunk_data = stream.read(globalvariables.SAMPLES_PER_CHUNK)
		except IOError, e:
			if e.args[1] == pyaudio.paInputOverflowed:
				chunk_data = '\x00'*globalvariables.SAMPLES_PER_CHUNK
			else:
				raise
		slid_win.append(abs(audioop.avg(chunk_data, 2)))
		full_recording.append(chunk_data)
		slid_win_average = averageLevel(slid_win)
		print "Average of window: " + str(slid_win_average) + " threshold: " + str(THRESHOLD)

		if slid_win_average <= THRESHOLD:
			if recording_started:
				print "-----------Stopped recording due to stopped speaking-----------"
				break
			else:
				if len(full_recording) > globalvariables.PRE_CHUNKS:
					full_recording.pop(0)
				if time.time() - listening_start_time > 5:
					print "--------Stopped recording as nothing heard--------"
					full_recording = []
					break
		else:
			if not recording_started:
				print("starting to record")
				face_controller.update(message="I'm listening...")
				recording_started = True

		if len(full_recording) >= max_recording_chunks:
			print "-----------Stopped recording due to max recording length-----------"
			break

	stream.stop_stream()
	face_controller.update(message="Hang on, I'm Thinking...")
	play_wav(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'raw/soundstop.wav'))

	if len(full_recording):
		wav_filename = save_speech(full_recording,p)
		flac_filename = convert_wav_to_flac(wav_filename)
		return flac_filename
	else:
		return ""


def save_speech(data, p):
	filename = os.path.join(os.path.dirname(os.path.realpath(__file__)),'output_'+str(int(time.time())))
	# write data to WAVE file
	data = ''.join(data)
	wf = wave.open(filename+'.wav', 'wb')
	wf.setnchannels(1)
	wf.setsampwidth(p.get_sample_size(globalvariables.FORMAT))
	wf.setframerate(globalvariables.SAMPLERATE)
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
	import googlewebspeech
	# Unit test when module is run
	rospy.init_node("flac_record")
	stream = open_stream()
	calibrate_input_threshold(stream)
	filename = listen_for_block_of_speech(stream)
	if filename:
		os.system('mplayer ' + filename)
		print googlewebspeech.stt_google_wav(filename)
		# os.remove(filename)
