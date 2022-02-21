#!/usr/bin/env python3

import os 

from kivy.app import App
from kivy.config import Config
from kivy.lang import Builder
from kivy.logger import Logger as log
from kivy.uix.screenmanager import ScreenManager

from deskformer_ui.screens import MainScreen


class CustomScreenManager(ScreenManager):
    def __init__(self, *args, **kwargs):
        super(CustomScreenManager, self).__init__(*args, **kwargs)
        self.previous_screen_name = None

    def on_current(self, instance, value):
        self.previous_screen_name = (
            self.current_screen.name if self.current_screen else None
        )
        return super(CustomScreenManager, self).on_current(instance, value)


class DeskFormerApp(App):
    def load_kv(self, *args, **kwargs):
        for f in [
            "styles",
            "screens/main",
        ]:
            Builder.load_file(os.path.join("deskformer_ui/uix", f + ".kv"))

    def build(self):
        self.sm = CustomScreenManager()

        self.main_screen = MainScreen(name="main")
        self.sm.add_widget(self.main_screen)

        return self.sm

    def on_stop(self):
        log.info("Stopping the app...")