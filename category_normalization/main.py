import itertools
import re
from typing import List

import inflect
import numpy as np
from spellchecker import SpellChecker
import pandas as pd
from textblob import Word


def is_word_with_errors(word: str) -> bool:
    if not word:
        return False
    candidates = [spell.candidates(spells) if spell.candidates(spells) is not None else [] for spells in
                  spell.unknown(spell.split_words(word))]
    merged = list(itertools.chain(*candidates))
    return not not merged


def normalize_category(category_string: str) -> str:
    sub = re.sub('[^A-Za-z0-9]+', '', category_string.replace('&', 'and').lower())
    return sub


SPECIAL_CHARS = '!@#$%^&*()-+?_=,<>/"'
SPACE_STRING = ' '

df = pd.read_excel("C:\\Users\\proje\\Downloads\\SKU-Mapping-Final-Publication-20230720.xlsx")
df = df.fillna('')
columns = list(filter(lambda x: str(x).lower().startswith('l'), df.columns))
spell = SpellChecker()
inflect = inflect.engine()

unique_values = {v: normalize_category(v) for v in
                 list(itertools.chain(*[list(filter(lambda x: x != '', df[c].unique())) for c in columns]))}

rev_dict = {}
for key, value in unique_values.items():
    rev_dict.setdefault(value, set()).add(key)

result = set(itertools.chain.from_iterable(
    values for key, values in rev_dict.items()
    if len(values) > 1))

errors = dict()

for column in columns:
    for value in filter(lambda x: str(x) != '', df[column].unique()):
        if ' and ' in value:
            errors.update({value: 'background-color: green'})
            print(f'and start with lower case. {value}')
        elif any(c in SPECIAL_CHARS for c in value):
            errors.update({value: 'background-color: yellow'})
            print(f'has special char. {value}')
        elif value.startswith(SPACE_STRING) or value.endswith(SPACE_STRING):
            errors.update({value: 'background-color: blue'})
            print(f'value has spaces in the end or start {value}.')
        elif list(filter(lambda x: x.endswith(SPACE_STRING) or x.startswith(SPACE_STRING), value.split(SPACE_STRING))):
            errors.update({value: 'background-color: brown'})
            print(f'word in value has extra spaces. {value}')
        elif value in result:
            errors.update({value: 'background-color: darkblue'})
            print(f'word has almost same value. {value}')
        # elif is_word_with_errors(value):
        #     errors.update({value: 'background-color: orange'})
        #     print(f'spell check error {value}.')

styled = df.style.applymap(lambda x: errors.get(x, None))
styled.to_excel(
    'C:\\Users\\proje\\PycharmProjects\\python_migration_data_tool\\category_normalization\\test.xlsx',
    engine='openpyxl')
