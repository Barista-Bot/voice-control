#!/usr/bin/env python2
import pyaudio
import wave
import audioop
from collections import deque
from googletext2speech import play_wav
import os
import time
import globalvariables
import numpy as np
import rospy
import std_srvs.srv
from face.msg import faceRequests
from user_identification import client as faceidclient

visual_talkingness = 0
visual_talkingness_history_len = 10
visual_talkingness_history = deque(maxlen=visual_talkingness_history_len)
visual_talkingness_passive_max = 0
visual_talkingness_passive_avg = 0
recording_override_start = False
recording_override_stop = False

def init_faceid_subscription():
    def face_id_callback(msg):
        global visual_talkingness, visual_talkingness_history
        if msg.is_person:
            visual_talkingness = msg.talkingness
            visual_talkingness_history.append(visual_talkingness)

    faceidclient.subscribe(face_id_callback)

def init_ros_override_services():
    pkg_name = 'voice_control'

    def recording_start_callback(r):
        global recording_override_start
        recording_override_start = True
        return std_srvs.srv.EmptyResponse()
    def recording_stop_callback(r):
        global recording_override_stop
        recording_override_stop = True
        return std_srvs.srv.EmptyResponse()

    rospy.Service(pkg_name+'/recording_start', std_srvs.srv.Empty, recording_start_callback)
    rospy.Service(pkg_name+'/recording_stop', std_srvs.srv.Empty, recording_stop_callback)

def open_stream():
    global p
    p = pyaudio.PyAudio()
    try:
        stream = p.open(format = globalvariables.FORMAT, channels = globalvariables.CHANNELS, rate = globalvariables.SAMPLERATE, input = True, input_device_index = find_input_device(p), frames_per_buffer = globalvariables.SAMPLES_PER_CHUNK)
    except IOError, e:
        if e.args[1] == pyaudio.paInvalidSampleRate:
            globalvariables.SAMPLERATE = 44100
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

def calibrate_input_threshold(stream=None):
    print "-----------Calibrating-----------"

    while len(visual_talkingness_history) < visual_talkingness_history_len:
        time.sleep(0.01)

    print list(visual_talkingness_history)

    global visual_talkingness_passive_max, visual_talkingness_passive_avg
    visual_talkingness_passive_max = max(visual_talkingness_history)
    visual_talkingness_passive_avg = np.mean([np.mean(visual_talkingness_history), visual_talkingness_passive_max])

    print "----------- max: " + str(visual_talkingness_passive_max) + " avg: " + str(visual_talkingness_passive_avg) + "-----------"
        

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
    global recording_override_start
    global recording_override_stop

    interaction_cancelled = False
    recording_override_start = False
    recording_override_stop = False

    full_recording = []
    max_recording_chunks = 8 * globalvariables.CHUNKS_PER_SECOND
    face_controller = FaceController()
    calibrate_input_threshold()
    recording_started = False
    
    beep_start = time.time()
    stream.start_stream()
    play_wav(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'raw/soundstart.wav'))
    beep_end = time.time()
    print "Removing first " + str(int(globalvariables.SAMPLERATE*(beep_end - beep_start))) + " samples from recording"
    stream.read(int(globalvariables.SAMPLERATE*(beep_end - beep_start)))
    prev_visual_talkingness = 0
    
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
        full_recording.append(chunk_data)

        print "Visual talkingness: " + str(visual_talkingness)

        if recording_started:
            if not recording_override_start:
                if visual_talkingness <= visual_talkingness_passive_avg:
                    print "-----------Stopped recording due to stopped speaking-----------"
                    break
        else:
            if visual_talkingness > visual_talkingness_passive_max or recording_override_start:
                print("starting to record")
                face_controller.update(message="I'm listening...")
                recording_started = True
            else:
                if len(full_recording) > globalvariables.PRE_CHUNKS:
                    full_recording.pop(0)
                if time.time() - listening_start_time > 5:
                    print "--------Stopped recording as nothing heard--------"
                    full_recording = []
                    break
        
        if recording_override_stop:
            print "-----------Stopped recording due to override-----------"
            break

        if len(full_recording) >= max_recording_chunks:
            print "-----------Stopped recording due to max recording length-----------"
            break

    stream.stop_stream()
    face_controller.update(message="Hang on a moment...")
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
    init_faceid_subscription()
    init_ros_override_services()
    # calibrate_input_threshold(stream)
    filename = listen_for_block_of_speech(stream)
    if filename:
        os.system('mplayer ' + filename)
        print googlewebspeech.stt_google_wav(filename)
        # os.remove(filename)
