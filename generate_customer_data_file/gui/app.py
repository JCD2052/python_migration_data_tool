import traceback

from data_migration.gui.app import LABEL_WIDTH, LABEL_HEIGHT, WRAP_LENGTH
from utils.color_constants import BLUE_COLOR, WHITE_COLOR
from utils.data_type_constant import *
from tkinter import ttk, Button, filedialog, Label
from generate_customer_data_file.data.type_options import brands
from utils.label_logger import LabelLogger

SELECT_BRAND = 'Select Brand'

APP_TITLE = 'Create Data for Loading Tool'
START_WINDOW_GEOMETRY = '300x300'
AFTER_SELECTION_WINDOW_GEOMETRY = '1024x768'
SUBMIT_HEIGHT = 2
SUBMIT_WIDTH = 10
DEFAULT_COLUMN = 1
COUNT = 20
TXT_FILE_EXTENSION = '.txt'


class GenerateCustomerFileApp:
    def __init__(self) -> None:
        self.__window = tkinter.Tk()
        self.__select_company_dropdown = tkinter.ttk.Combobox(self.__window, values=[d.brand_name for d in brands])
        self.select_brand_label = tkinter.Label(self.__window,
                                                text=f'{SELECT_BRAND}:',
                                                fg=BLUE_COLOR, background=WHITE_COLOR)
        self.__select_brand_button = Button(self.__window,
                                            text=SELECT_BRAND,
                                            width=SUBMIT_WIDTH, height=SUBMIT_HEIGHT,
                                            command=self.__set_brand_content_on_selected_brand_name)
        self.__brand_content = None
        self.__generate_address_button = None
        self.__submit_button = None
        self.__browse_save_directory_button = None
        self.__status_label = None
        self.__save_directory = None

    def run(self) -> None:
        self.__configure_app()
        self.__start_grid_configuration()
        self.__window.mainloop()

    def __start_grid_configuration(self) -> None:
        self.select_brand_label.grid(column=0, row=1)
        self.__select_company_dropdown.grid(column=0, row=2)
        self.__select_brand_button.grid(column=0, row=3)

    def __configure_app(self) -> None:
        self.__window.title(APP_TITLE)
        self.__window.geometry(START_WINDOW_GEOMETRY)
        self.__window.config(background=WHITE_COLOR)

    def __submit(self) -> None:
        try:
            if self.__save_directory is None:
                raise Exception("Didn't select a save folder")
            data = self.__brand_content.get_values_from_input_widgets()
            file_name = self.__brand_content.get_file_name()
            path = f'{self.__save_directory}//{file_name}' + TXT_FILE_EXTENSION
            with open(path, mode='w') as file:
                file.write(data)
            self.__status_label.info(f'Saved to {path}')
        except Exception:
            self.__status_label.error(f"ERROR. SOMETHING WENT WRONG: {traceback.format_exc()}")

    def __set_brand_content_on_selected_brand_name(self) -> None:
        self.__remove_primal_widgets()
        selected_brand = self.__select_company_dropdown.get()
        data = list(filter(lambda x: selected_brand == x.brand_name, brands))[0]
        self.__window.geometry(AFTER_SELECTION_WINDOW_GEOMETRY)
        self.__brand_content = data.class_type(self.__window, data)
        self.__brand_content.create_labels()
        self.__configure_grid_according_to_selected_brand()

    def __select_save_directory(self) -> None:
        self.__save_directory = filedialog.askdirectory()

    def __remove_primal_widgets(self) -> None:
        widgets = {k: v for k, v in self.__dict__.items() if
                   issubclass(type(v), tkinter.Widget) and not None}.keys()
        for widget in widgets:
            self.__getattribute__(widget).grid_remove()

    def __configure_grid_according_to_selected_brand(self) -> None:
        widgets = {k: v for k, v in self.__brand_content.__dict__.items() if
                   issubclass(type(v), tkinter.Widget) and not None}.keys()
        for index, widget in enumerate(widgets):
            column = int(index / COUNT)
            row = index % COUNT
            self.__brand_content.__getattribute__(widget).grid(column=column, row=row)
            self.__window.columnconfigure(column, weight=2)

        current_grid_size = self.__window.grid_size()
        center_column = int(current_grid_size[0] / 2)
        current_row = current_grid_size[1]
        self.__generate_address_button = tkinter.Button(self.__window,
                                                        text="Generate addresses",
                                                        width=20, height=SUBMIT_HEIGHT,
                                                        command=self.__brand_content.generate_address)
        self.__submit_button = tkinter.Button(self.__window,
                                              text="Submit",
                                              width=SUBMIT_WIDTH, height=SUBMIT_HEIGHT,
                                              command=self.__submit)
        self.__browse_save_directory_button = Button(self.__window,
                                                     text="Select Directory",
                                                     command=self.__select_save_directory)
        self.__status_label = LabelLogger(Label(self.__window,
                                                text='',
                                                width=100, height=10,
                                                fg=BLUE_COLOR, background=WHITE_COLOR,
                                                wraplength=WRAP_LENGTH))
        self.__submit_button.grid(column=center_column, row=current_row)
        self.__generate_address_button.grid(column=center_column, row=current_row + 1)
        self.__browse_save_directory_button.grid(column=center_column, row=current_row + 2)
        self.__status_label.element.grid(column=center_column, row=current_row + 5)
