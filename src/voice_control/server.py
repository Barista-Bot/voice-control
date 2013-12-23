#!/usr/bin/env python2
import signal
import rospy
import std_srvs.srv
import time
import userdb
from user_identification import client as faceidclient
import interaction
import face


class VoiceControlServer(object):
    NODE_NAME = 'voice_control'

    def __init__(self):
        rospy.init_node(self.NODE_NAME)

        self.interaction_started = False
        self.facemsg = None
        self.interaction = None

        faceidclient.subscribe(self.faceidmsg_callback)
        rospy.Service(self.NODE_NAME+'/start', std_srvs.srv.Empty, self.start_interaction_callback)
        interaction.init()

        signal.signal(signal.SIGINT, self.exit)

    def exit(self, *args):
        print 'Exiting'
        raise SystemExit(0)

    def faceidmsg_callback(self, msg):
        self.facemsg = msg

    def start_interaction_callback(self, in_data):
        self.interaction_started = True
        return std_srvs.srv.EmptyResponse()

    def user_of_face(self, db):
        if self.facemsg.is_known_person:
            user = db.getUser(self.facemsg.id)
            user.n_visits += 1
            print "Found existing person",
        else:
            user = db.newUser()
            print "Created new person",

        print "ID:", str(user.id), "Level:", str(user.level)
        return user

    def main(self):
        while not rospy.is_shutdown():
            if self.interaction_started:
                if self.facemsg is not None and self.facemsg.is_person:
                    with userdb.open() as db:
                        user = self.user_of_face(db)
                        self.interaction = interaction.Interaction(user=user)
                        self.interaction.main()
                    self.interaction_started = False
                else:
                    print "Looking for face"
            else:
                print "Waiting to start"
            time.sleep(0.5)


