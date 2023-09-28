from abc import ABC, abstractmethod
from asyncio import Future
from concurrent.futures import ThreadPoolExecutor
from typing import Any, List, Iterable, Dict, Tuple

from pandas.io.formats.style import Styler

from pandas import DataFrame, Series

from category_normalization.validators.almost_same_word_validator import AlmostSameWordValidator
from category_normalization.validators.base_validator import BaseValidator, LowerAndValidator, \
    SpecialCharactersValidator, ExtraSpacesValidator, NonBreakingSpaceValidator, UpperMPInSkuValidator
from category_normalization.validators.check_category_validator import CheckCategoryHierarchyValidator
from category_normalization.validators.duplicate_in_column_validator import DuplicatesInColumnValidator
from category_normalization.validators.duplicate_sku_validator import DuplicateInSkuValidator
from category_normalization.validators.spell_check_validator import SpellCheckValidator
from category_normalization.validators.wrong_hierarchy_validator import DuplicateInTheLastCategoryValidator
from utils.label_logger import LabelLogger

SKU_COLUMN_NAME = "MPSku"


class BaseFileValidationStrategy(ABC):
    def __init__(self, data_frame: DataFrame, label_logger: LabelLogger) -> None:
        self._label_logger = label_logger
        self._data_frame: DataFrame = data_frame
        self._category_columns: List[str] = list(
            filter(lambda column: str(column).lower().startswith('l'),
                   self._data_frame.columns))
        self._errors_frame: List[Dict[str, str]] = []
        self._validated_frame: Dict[str, str] = dict()
        self._legend_frame: Dict[str, Tuple[str, str]] = dict()

    @abstractmethod
    def process(self) -> None:
        pass

    def get_validated_frame(self) -> Styler:
        return self._data_frame.style.applymap(lambda cell: self._validated_frame.get(cell, None))

    def get_errors_frame(self) -> Styler:
        return DataFrame(self._errors_frame).style.applymap(lambda cell: self._validated_frame.get(cell, None))

    def get_legend_frame(self) -> Styler:
        sorted_dict = dict()
        values = list(self._legend_frame.values())
        sorted_value_index = sorted(values, key=lambda t: t[1])
        for count, val in enumerate(sorted_value_index):
            for k, v in self._legend_frame.items():
                if val == v:
                    sorted_dict.update({f"Priority {int(count) + 1}: {k}": v[0]})
        values = [{"Validation criteria": cell[0]} for cell in sorted_dict.items()]
        return DataFrame(values).style.applymap(lambda cell: sorted_dict.get(cell, None))

    @abstractmethod
    def _build_validators(self) -> List[BaseValidator]:
        pass

    def _proceed_values(self, values: Iterable[Any], validators: List[BaseValidator]):
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures: List[Future] = [executor.submit(self._check_value, value, validators) for value in
                                     values]
            [call.result() for call in futures]

    def _check_value(self, category_value: str, validators: List[BaseValidator]):
        self._label_logger.info(f'Checking value {category_value}...')
        failed_validators = []
        messages = []
        for val in validators:
            res = val.validate(category_value)
            if res[0]:
                failed_validators.append(val)
                messages.append(res[1])
        failed_validators.sort(key=lambda x: x.get_priority())
        if failed_validators:
            bg_color = failed_validators[0].get_background_color()
            self._errors_frame.append({"Value": category_value, "Reason": ". ".join(messages)})
            self._validated_frame.update({category_value: bg_color})

    def _collect_legend_info(self, validators: List[BaseValidator]) -> None:
        for validator in sorted(validators, key=lambda x: x.get_priority()):
            validator_data = {validator.get_name(): (validator.get_background_color(), validator.get_priority())}
            self._legend_frame.update(validator_data)


class TaxonomyFileValidationStrategy(BaseFileValidationStrategy):
    def process(self) -> None:
        validators: List[BaseValidator] = self._build_validators()
        for column in self._category_columns:
            values: List[str] = list(filter(lambda x: str(x), self._data_frame[column].unique()))
            self._collect_legend_info(validators)
            self._proceed_values(values, validators)

    def _build_validators(self) -> List[BaseValidator]:
        return [LowerAndValidator(),
                SpecialCharactersValidator(),
                ExtraSpacesValidator(),
                NonBreakingSpaceValidator(),
                SpellCheckValidator(),
                AlmostSameWordValidator(self._data_frame),
                DuplicatesInColumnValidator(self._data_frame),
                CheckCategoryHierarchyValidator(self._data_frame),
                DuplicateInTheLastCategoryValidator(self._data_frame)]


class SkuMappingFileValidationStrategy(TaxonomyFileValidationStrategy):
    def __init__(self, data_frame: DataFrame, label_logger: LabelLogger) -> None:
        super().__init__(data_frame, label_logger)
        self._data_frame: DataFrame = self._data_frame[self._category_columns]
        self._sku_values: Series = data_frame[SKU_COLUMN_NAME]
        self.__sku_frame: DataFrame = self._sku_values.to_frame(SKU_COLUMN_NAME)

    def process(self) -> None:
        super().process()
        values = filter(lambda v: bool(v), self._sku_values)
        validators = self.__build_sku_validators()
        self._collect_legend_info(validators)
        self._proceed_values(values, validators)
        self._data_frame = self.__sku_frame.join(self._data_frame)

    def _build_validators(self) -> List[BaseValidator]:
        return [LowerAndValidator(),
                SpecialCharactersValidator(),
                ExtraSpacesValidator(),
                NonBreakingSpaceValidator(),
                SpellCheckValidator(),
                AlmostSameWordValidator(self._data_frame),
                DuplicatesInColumnValidator(self._data_frame),
                CheckCategoryHierarchyValidator(self._data_frame)]

    def __build_sku_validators(self):
        return [UpperMPInSkuValidator(),
                DuplicateInSkuValidator(self._sku_values),
                ExtraSpacesValidator(),
                NonBreakingSpaceValidator(),
                AlmostSameWordValidator(self.__sku_frame)]
