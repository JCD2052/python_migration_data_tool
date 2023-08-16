import tkinter
from datetime import datetime
from tkinter import Label

from utils.data_type_constant import data_types
from utils.color_constants import BLUE_COLOR, WHITE_COLOR

LABEL_HEIGHT = 2
LABEL_WIDTH = 80
SUBMIT_HEIGHT = 2
SUBMIT_WIDTH = 10
WRAP_LENGTH = 600


# Generic class for data
class DataLoad:
    _FILE_NAME = None

    def __init__(self, window, data_load) -> None:
        self.window = window
        self.data_load = data_load

    # Get values from all input elements and join them by delimiter
    def get_values_from_input_widgets(self) -> str:
        widgets = {k: v for k, v in self.__dict__.items() if type(v) in data_types.keys() and not None}
        values = []
        for k, v in widgets.items():
            widget = self.__getattribute__(k)
            values.append(str(widget.get()))
        print(values)
        return '|'.join(values)

    # For every input element create label
    def create_labels(self) -> None:
        widgets = {k: v for k, v in self.__dict__.items() if issubclass(type(v), tkinter.Widget) and not None}
        for name, element_type in widgets.items():
            try:
                text = f'{data_types[type(element_type)]} {name.lower().replace("_", " ")}:'
                self.__delattr__(name)
                self.__setattr__(f'{name}_label', self._create_label_element(text, self.window))
                self.__setattr__(name, element_type)
            except KeyError:
                pass

    # Create text input element
    def _create_text_input(self) -> tkinter.Entry:
        return tkinter.Entry(self.window, width=50)

    # Create file name according to data type
    @classmethod
    def get_file_name(cls) -> str:
        return f'{cls._FILE_NAME}_{cls.__get_current_time()}'

    # Create label element
    @staticmethod
    def _create_label_element(text, window) -> tkinter.Label:
        return Label(window,
                     text=text,
                     width=LABEL_WIDTH, height=LABEL_HEIGHT,
                     fg=BLUE_COLOR, background=WHITE_COLOR,
                     wraplength=WRAP_LENGTH)

    # Get current time in specific format
    @staticmethod
    def __get_current_time() -> str:
        now = datetime.now()
        return now.strftime("%Y%m%d%H%M%S")
