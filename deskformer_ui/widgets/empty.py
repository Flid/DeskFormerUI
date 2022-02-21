from kivy.uix.widget import Widget
from kivy.logger import Logger as log
from kivy.properties import ObjectProperty
from kivy.uix.gridlayout import GridLayout

from deskformer_ui.widgets.ui_debugger import UIDebugger

from .widgetbase import DFWidgetBase


class DFEmptyWidget(DFWidgetBase):
    split_button = ObjectProperty()

    def split_widget(self, rows, cols):
        log.info(self)
        self.remove_widget(self.ids.split_button)
        grid = GridLayout(
            rows=rows, 
            cols=cols,
            size_hint=(1, 1), 
            pos_hint={'x': 0, 'y': 0},
        )

        for x in range(rows):
            for y in range(rows):
                grid.add_widget(DFEmptyWidget())
        
        self.add_widget(grid)

    def replace_widget(self):
        pass