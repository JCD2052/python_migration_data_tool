import pandas as pd


class ReadExcel:
    def __init__(self, path):
        self.path = path

    def get_records(self):
        return self.open_file().to_dict('records')

    def open_file(self, sheet_name=None):
        if sheet_name is None:
            return pd.read_excel(self.path)
        else:
            return pd.read_excel(self.path, sheet_name=sheet_name)
