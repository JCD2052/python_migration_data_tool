from tkinter import Label

from utils.color_constants import BLUE_COLOR, RED_COLOR


# Simple class wrapper for the 'tkinter.Label' class.
class LabelLogger:
    def __init__(self, label_element: Label) -> None:
        self.element = label_element

    # Show message with an info color
    def info(self, message: str) -> None:
        self.element.configure(text=message, fg=BLUE_COLOR)

    # Show message with an error color
    def error(self, message: str) -> None:
        self.element.configure(text=message, fg=RED_COLOR)
