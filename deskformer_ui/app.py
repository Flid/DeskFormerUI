#!/usr/bin/env python3

import os

from kivy.app import App
from kivy.config import Config
from kivy.lang import Builder
from kivy.logger import Logger as log

from deskformer_ui.screens import MainScreen


class DeskFormerApp(App):
    def load_kv(self, *args, **kwargs):
        for root, dirs, files in os.walk("deskformer_ui/uix"):
            for f in files:
                if f.lower().endswith(".kv"):
                    Builder.load_file(os.path.join(root, f))

    def build(self):
        self.root = MainScreen()

    def on_stop(self):
        log.info("Stopping the app...")
