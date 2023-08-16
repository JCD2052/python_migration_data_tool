import tkinter
from datetime import datetime
from tkinter import Label

from generate_customer_data_file.data.data_address import RandomAddressGenerator
from utils.data_type_constant import data_types
from utils.color_constants import BLUE_COLOR, WHITE_COLOR

LABEL_HEIGHT = 2
LABEL_WIDTH = 80
SUBMIT_HEIGHT = 2
SUBMIT_WIDTH = 10
WRAP_LENGTH = 600


class DataLoad:
    _FILE_NAME = None

    def __init__(self, window, data_load) -> None:
        self.window = window
        self.data_load = data_load

    def get_values_from_input_widgets(self) -> str:
        widgets = {k: v for k, v in self.__dict__.items() if type(v) in data_types.keys() and not None}
        values = []
        for k, v in widgets.items():
            widget = self.__getattribute__(k)
            values.append(str(widget.get()))
        print(values)
        return '|'.join(values)

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

    def generate_address(self) -> None:
        random_address = RandomAddressGenerator()
        self.billing_address_street_name.delete(0, 'end')
        self.billing_address_street_name.insert(0, random_address.address_line)
        self.billing_address_postal_code.delete(0, 'end')
        self.billing_address_postal_code.insert(0, random_address.zip_code)
        self.billing_address_town.delete(0, 'end')
        self.billing_address_town.insert(0, random_address.city)
        self.billing_address_country.delete(0, 'end')
        self.billing_address_country.insert(0, random_address.country)
        self.billing_address_region.delete(0, 'end')
        self.billing_address_region.insert(0, random_address.state)
        self.billing_address_email.delete(0, 'end')
        self.billing_address_email.insert(0, random_address.address_email)

        self.shipping_address_street_name.delete(0, 'end')
        self.shipping_address_street_name.insert(0, random_address.address_line)
        self.shipping_address_postal_code.delete(0, 'end')
        self.shipping_address_postal_code.insert(0, random_address.zip_code)
        self.shipping_address_town.delete(0, 'end')
        self.shipping_address_town.insert(0, random_address.city)
        self.shipping_address_country.delete(0, 'end')
        self.shipping_address_country.insert(0, random_address.country)
        self.shipping_address_region.delete(0, 'end')
        self.shipping_address_region.insert(0, random_address.state)
        self.shipping_address_email.delete(0, 'end')
        self.shipping_address_email.insert(0, random_address.address_email)

    def _create_text_input(self) -> tkinter.Entry:
        return tkinter.Entry(self.window, width=50)

    @classmethod
    def get_file_name(cls) -> str:
        return f'{cls._FILE_NAME}_{cls.__get_current_time()}'

    @staticmethod
    def _create_label_element(text, window) -> tkinter.Label:
        return Label(window,
                     text=text,
                     width=LABEL_WIDTH, height=LABEL_HEIGHT,
                     fg=BLUE_COLOR, background=WHITE_COLOR,
                     wraplength=WRAP_LENGTH)

    @staticmethod
    def __get_current_time() -> str:
        now = datetime.now()
        return now.strftime("%Y%m%d%H%M%S")
