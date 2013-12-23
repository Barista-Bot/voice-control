#!/usr/bin/env python2

import time
import itertools
import threading
import playback
import recording
import wit
import face


speaker = None


def init():
    global speaker
    speaker = Speaker()
    recording.init(face_controller=speaker.face_controller)


class Speaker(object):
    def __init__(self):
        self.face_controller = face.client.Controller()
        self.lock = threading.Lock()

    def interrupt(self):
        self.interrupted = True

    def say(self, text):
        self.lock.acquire()
        try:
            self.interrupted = False
            print "Saying:", text
            self.face_controller.update(is_talking=True, message=text)
            playback.say(text, lambda:self.interrupted)
        finally:
            self.face_controller.clear()
            self.lock.release()


class Interaction(object):
    def __init__(self, user):
        self.user = user
        self.responses = BaristaResponses(self)
        self.ended = False

    def user_responses(self):
        while not self.ended:
            try:
                speech_text = recording.listener.get_speech_from_user_as_text()
                print "Heard " + speech_text
                wit_response = wit.query(speech_text)
                yield wit_response
            except recording.SpeechNotHeardException:
                yield {'intent':'unknown'}
            except recording.SpeechNotTextifiedException:
                yield {'intent':'unknown'}
            except wit.SpeechNotUnderstoodException:
                yield {'intent':'unknown'}

    def end(self):
        self.ended = True

    def say(self, text):
        speaker.say(text)

    def set_user_name(self, name):
        name = name.title()
        print "Setting user " + str(self.user.id) + "'s name to " + name
        self.user.name = name
        
    def main(self):
        for i in itertools.chain([{'intent':'init'}], self.user_responses()):
            out_response = self.responses[i]
            out_response.pre_action()
            self.say(out_response.speech)
            out_response.post_action()
            self.prev_response = out_response


def enum(*items):
    enums = dict(zip(items, range(len(items))))
    return type('Enum', (), enums)


class BaristaResponses(object):
    def __init__(self, interaction):
        self.interaction = interaction

    def __getitem__(self, wit_response):
        try:
            intent = wit_response['intent']
        except KeyError:
            intent = 'unknown'

        try:
            entities = wit_response['entities']
        except KeyError:
            entities = None

        return getattr(self, 'if_intent_'+intent)(entities)

    def if_intent_init(self, ent):
        try:
            return self.Response(self.Id.ask_how_user_is, "Hello again " + self.interaction.user.name + ", how are you?")
        except AttributeError:
            return self.Response(self.Id.say_hello, "Hi! I'm Barista Bot. Speak after the tone.")

    def if_intent_hello(self, ent):
        return self.if_intent_init(ent)

    def if_intent_emotion(self, ent):
        return self.Response(None, "That's nice.")

    def if_intent_name(self, ent):
        try:
            name = ent['contact']['value']
        except KeyError:
            return self.didnt_understand()
        action = lambda: self.interaction.set_user_name(name)
        return self.Response(None, "It's nice to meet you "+name, pre_action=action)

    def if_intent_good_bye(self, ent):
        return self.Response(self.Id.say_goodbye, "Goodbye", post_action=self.interaction.end)

    def if_intent_unknown(self, ent):
        return self.didnt_understand()

    def didnt_understand(self):
        return self.Response(None, "Sorry, could you repeat that?")

    class Response(object):
        def __init__(self, id, speech, pre_action=lambda:None, post_action=lambda:None):
            self.id = id
            self.speech = speech
            self.pre_action = pre_action
            self.post_action = post_action

    Id = enum(
        'say_hello',
        'ask_how_user_is',
        'ask_for_name',
        'say_goodbye',
    )
                 

    
