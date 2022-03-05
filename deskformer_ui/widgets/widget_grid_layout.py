from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import AliasProperty, ObjectProperty
from kivy.logger import Logger as log
from kivy.clock import Clock
from deskformer_ui.widgets import DFWidgetBase
from deskformer_ui.widgets.ui_debugger import add_debugging


class WidgetGridLayout(RelativeLayout):
    GRID_COUNT = (16, 9)
    cell_width = AliasProperty(
        lambda self: self.width / WidgetGridLayout.GRID_COUNT[0],
        None,
        bind=["width"],
    )

    cell_height = AliasProperty(
        lambda self: self.height / WidgetGridLayout.GRID_COUNT[1],
        None,
        bind=["height"],
    )
    widget_selector = ObjectProperty(None)

    def __init__(self, **kw):
        super().__init__(**kw)

    def change_lock_state(self):
        pass

    def show_add_window(self):
        self.widget_selector.show_widget()

    def ids_to_widget_size(self, horiz, vert):
        return horiz * self.cell_width, vert * self.cell_height


class WidgetSelector(RelativeLayout):
    widget_list = ObjectProperty(None)

    def __init__(self, **kw):
        super().__init__(**kw)
        Clock.schedule_once(self.hide_widget)

    def hide_widget(self, *args):
        self._size_hint_y_backup = self.size_hint_y
        self.size_hint_y = 0
        self.opacity = 0
        self.disabled = True

    def show_widget(self, *args):
        self.size_hint_y = self._size_hint_y_backup
        self.opacity = 1
        self.disabled = False
        add_debugging(self.widget_list, (1, 0, 0))
        self._initialize_widgets_once()

    def _initialize_widgets_once(self):
        if hasattr(self, "_widgets_initialized"):
            return

        for widget_cls in DFWidgetBase.__subclasses__():
            log.info("Loading widget %s...", widget_cls.__name__)
            self.widget_list.add_widget(WidgetSelectorSingleItem(self, widget_cls))

        # self._widgets_initialized = True


class WidgetSelectorSingleItem(RelativeLayout):
    def __init__(self, widget_selector, widget_cls, **kw):
        self.widget_cls = widget_cls
        self.widget_selector = widget_selector

        super().__init__(**kw)

        add_debugging(self)
        self._load_widget()

    def _load_widget(self):
        self.ids.label.text = self.widget_cls.get_title()
        self.ids.image.source = self.widget_cls.get_icon_path()
