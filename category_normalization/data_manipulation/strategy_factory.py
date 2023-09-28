from pandas import DataFrame

from category_normalization.data_manipulation.file_validation_strategy import BaseFileValidationStrategy, \
    SkuMappingFileValidationStrategy, TaxonomyFileValidationStrategy, SKU_COLUMN_NAME
from utils.label_logger import LabelLogger


class StrategyFactory:
    @staticmethod
    def get_strategy(data: DataFrame, label_logger: LabelLogger) -> BaseFileValidationStrategy:
        if SKU_COLUMN_NAME in data.columns:
            return SkuMappingFileValidationStrategy(data, label_logger)
        else:
            return TaxonomyFileValidationStrategy(data, label_logger)
