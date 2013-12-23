#!/usr/bin/env python2

import os
import tempfile
import subprocess
import collections
import pyaudio
import simplejson
import requests
import wave
import time
import numpy as np
import playback
import roslib
import rospy
import std_srvs.srv
import user_identification

PKG_NAME = 'voice_control'

listener = None

def init(face_controller):
    global listener
    listener = SpeechListener(face_controller=face_controller)


class SpeechNotHeardException(Exception):
    pass
class SpeechNotTextifiedException(Exception):
    pass


class SpeechListener(object):
    SAMPLES_PER_SECOND = 44100
    SAMPLES_PER_CHUNK = 4096
    MAX_RECORDING_SECONDS = 8
    PRE_RECORDING_SECONDS = 1
    PYAUDIO_FORMAT = pyaudio.paInt16
    PYAUDIO_CHANNELS = 1
    CHUNKS_PER_SECOND = SAMPLES_PER_SECOND / SAMPLES_PER_CHUNK
    MAX_RECORDING_CHUNKS = MAX_RECORDING_SECONDS * CHUNKS_PER_SECOND
    PRE_RECORDING_CHUNKS = PRE_RECORDING_SECONDS*CHUNKS_PER_SECOND
    
    def __init__(self, face_controller):
        self.face_controller = face_controller
        print "--Opening PyAudio"
        self.pyaudio = pyaudio.PyAudio()
        print "--Opened PyAudio"
        self.talkingness_history = collections.deque(maxlen=10)

        self.istream = self.pyaudio.open(
            format = self.PYAUDIO_FORMAT,
            channels = self.PYAUDIO_CHANNELS,
            rate = self.SAMPLES_PER_SECOND,
            frames_per_buffer = self.SAMPLES_PER_CHUNK,
            input = True,
        )
        self.istream.stop_stream()

        self.start_beep_file = os.path.join(roslib.packages.get_pkg_dir(PKG_NAME), 'sounds', 'start_beep.wav')
        self.end_beep_file = os.path.join(roslib.packages.get_pkg_dir(PKG_NAME), 'sounds', 'end_beep.wav')

        rospy.Service(PKG_NAME+'/recording_start', std_srvs.srv.Empty, self.recording_start_callback)
        rospy.Service(PKG_NAME+'/recording_stop', std_srvs.srv.Empty, self.recording_stop_callback)

        user_identification.client.subscribe(self.face_analysis_callback)

    def recording_start_callback(self, msg):
        self.recording_override_start = True
        return std_srvs.srv.EmptyResponse()

    def recording_stop_callback(self, msg):
        self.recording_override_stop = True
        return std_srvs.srv.EmptyResponse()

    def face_analysis_callback(self, msg):
        if msg.is_person:
            self.talkingness_history.append(msg.talkingness)

    @property
    def talkingness(self):
        return self.talkingness_history[-1]
    
    def calibrate(self):
        print "Calibrating"

        while len(self.talkingness_history) < self.talkingness_history.maxlen:
            time.sleep(0.1)
        print list(self.talkingness_history)

        self.upper_thresh = max(self.talkingness_history)
        self.lower_thresh = np.mean([np.mean(self.talkingness_history), self.upper_thresh])

        print "Upper thresh: " + str(self.upper_thresh) + " Lower thresh: " + str(self.lower_thresh)

    def record_sound(self):
        try:
            self.istream.start_stream()
            while True:
                try:
                    yield self.istream.read(self.SAMPLES_PER_CHUNK)
                except IOError, e:
                    if e.args[1] == pyaudio.paInputOverflowed:
                        yield '\x00'*self.SAMPLES_PER_CHUNK
                    else:
                        raise
        finally:
            self.istream.stop_stream()

    def get_speech_from_user(self):
        self.recording_override_start = False
        self.recording_override_stop = False

        full_recording = []
        recording_started = False

        playback.play_file(self.start_beep_file)
        self.calibrate()
        self.face_controller.update(message="Speak now")
        listening_start_time = time.time()

        for chunk_data in self.record_sound():
            full_recording.append(chunk_data)

            print "Talkingness: " + str(self.talkingness)

            if recording_started:
                if not self.recording_override_start:
                    if self.talkingness <= self.lower_thresh:
                        print "Stopped recording due to stopped speaking"
                        break
            else:
                if self.talkingness > self.upper_thresh or self.recording_override_start:
                    print("starting to record")
                    self.face_controller.update(message="I'm listening")
                    recording_started = True
                else:
                    if len(full_recording) > self.PRE_RECORDING_CHUNKS:
                        full_recording.pop(0)
                    if time.time() - listening_start_time > 5:
                        print "Stopped recording as nothing heard"
                        full_recording = []
                        break
            
            if self.recording_override_stop:
                print "Stopped recording due to override"
                break

            if len(full_recording) >= self.MAX_RECORDING_CHUNKS:
                print "Stopped recording due to max recording length"
                break

        self.face_controller.clear()
        playback.play_file(self.end_beep_file)

        if len(full_recording) == 0:
            raise SpeechNotHeardException()

        full_recording = ''.join(full_recording)
        return full_recording

    def save_to_wave_file(self, data):
        file_d = tempfile.NamedTemporaryFile()
        wave_file = wave.open(file_d, 'wb')
        wave_file.setnchannels(self.PYAUDIO_CHANNELS)
        wave_file.setsampwidth(self.pyaudio.get_sample_size(self.PYAUDIO_FORMAT))
        wave_file.setframerate(self.SAMPLES_PER_SECOND)
        wave_file.writeframes(data)
        file_d.flush()
        return file_d

    def get_speech_from_user_as_wave_file(self):
        speech = self.get_speech_from_user()
        return self.save_to_wave_file(speech)

    def get_speech_from_user_as_flac_file(self):
        wav_file = self.get_speech_from_user_as_wave_file()
        wav_file.flush()
        flac_file_name = wav_file.name + '.flac'
        subprocess.check_call(['flac', '-fs', wav_file.name, '-o', flac_file_name])
        wav_file.close()
        return open(flac_file_name, 'rb')

    def get_speech_from_user_as_text(self):
        flac_file = self.get_speech_from_user_as_flac_file()
        text = self.flac_to_text(flac_file)
        flac_file.close()
        os.remove(flac_file.name)
        return text

    def flac_to_text(self, flac_file):
        url = 'https://www.google.com/speech-api/v1/recognize'
        query_params = {'lang': 'en-GB', 'maxresults': 1}
        headers = {'Content-type': 'audio/x-flac; rate='+str(self.SAMPLES_PER_SECOND)}
        response = requests.post(url, params=query_params, data=flac_file.read(), headers=headers)

        try:
            hypotheses = response.json()['hypotheses']
            return hypotheses[0]['utterance']
        except (IndexError, simplejson.scanner.JSONDecodeError):
            raise SpeechNotTextifiedException()


def test():
    import face, signal
    def exit(*args):
        raise SystemExit(0)
    signal.signal(signal.SIGINT, exit)

    rospy.init_node("recording_test")
    init(face_controller=face.client.Controller())
    print listener.get_speech_from_user_as_text()

if __name__ == "__main__":
    test()
