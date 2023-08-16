from utils.color_constants import BLUE_COLOR, RED_COLOR


class LabelLogger:
    def __init__(self, label_element):
        self.element = label_element

    def info(self, message):
        self.element.configure(text=message, fg=BLUE_COLOR)

    def error(self, message):
        self.element.configure(text=message, fg=RED_COLOR)
