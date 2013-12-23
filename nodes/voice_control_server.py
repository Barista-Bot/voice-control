#!/usr/bin/env python2

import voice_control.server

if __name__ == "__main__":
    server = voice_control.server.VoiceControlServer()
    server.main()