import itertools
import re

import pandas as pd

from category_normalization.validators.validators import *


def get_unique_values_from_data_frame(data_frame: pd.DataFrame) -> Set[str]:
    values = {v: normalize_category(v) for v in
              list(itertools.chain(*[list(filter(lambda x: x != '', data_frame[c].unique())) for c in columns]))}
    rev_dict = {}
    for k, v in values.items():
        rev_dict.setdefault(v, set()).add(k)

    return set(itertools.chain.from_iterable(
        values for key, values in rev_dict.items()
        if len(values) > 1))


def normalize_category(category_string: str) -> str:
    sub = re.sub('[^A-Za-z0-9]+', '', category_string.replace('&', 'and').lower())
    return sub


SPACE_STRING = ' '
df = pd.read_excel("C:\\Users\\proje\\Downloads\\SKU-Mapping-Final-Publication-20230720.xlsx")
df = df.fillna('')
columns = list(filter(lambda x: str(x).lower().startswith('l'), df.columns))
errors = dict()
validators = [LowerAndValidator(), SpecialCharactersValidator(), ExtraSpacesValidator(),
              ExtraSpacesBetweenWordsValidator(), AlmostSameWordValidator(get_unique_values_from_data_frame(df)),
              SpellCheckValidator()]

for column in columns:
    for value in filter(lambda x: str(x) != '', df[column].unique()):
        res = [validator for validator in validators if validator.validate(value)]
        res.sort(key=lambda x: x.get_priority(), reverse=True)
        if res:
            errors.update({value: res[0].get_background_color()})
styled = df.style.applymap(lambda x: errors.get(x, None))
styled.to_excel(
    'C:\\Users\\proje\\PycharmProjects\\python_migration_data_tool\\category_normalization\\test.xlsx',
    engine='openpyxl')
