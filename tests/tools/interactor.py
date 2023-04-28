#!/usr/bin/env python3

import sys
import os
import subprocess

'''Manages communication by parsing stdout and delivering stdin to another process'''

class Interactor:

    def __init__(self, cmd):
        self.cmd = cmd
        self.launched = False

    def launch(self):
        self.proc = subprocess.run(cmd.split(), shell=True, capture_output=True)
        self.launched = True
