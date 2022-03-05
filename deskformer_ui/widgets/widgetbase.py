from kivy.uix.relativelayout import RelativeLayout
from kivy.logger import Logger as log
import inspect
import os


class DFWidgetBase(RelativeLayout):
    DEFAULT_ICON = "deskformer_ui/static/UI-packs/basic/widget-no-icon.png"

    @classmethod
    def get_icon_path(cls):
        class_dir = os.path.dirname(inspect.getfile(cls))
        icon_path = os.path.join(class_dir, "icon.png")
        if os.path.exists(icon_path):
            return icon_path

        return cls.DEFAULT_ICON

    @classmethod
    def get_title(cls):
        return cls.__name__
