from kivy.uix.widget import Widget
from kivy.properties import ColorProperty
from kivy.graphics.context_instructions import Color
from kivy.graphics import Line
from kivy.clock import Clock


class UIDebugger(Widget):
    color = ColorProperty(defaultvalue="red")


def add_debugging(widget, color=(1, 0, 1)):
    def _update(*args):
        with widget.canvas.after:
            Color(rgb=color)
            Line(
                rectangle=(
                    widget.x + 1,
                    widget.y + 1,
                    widget.width - 1,
                    widget.height - 1,
                ),
                dash_offset=5,
                dash_length=3,
            )

    Clock.schedule_once(_update)
