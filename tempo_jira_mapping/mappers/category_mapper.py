from tempo_jira_mapping.mappers.task_mapper import TaskMapper
from tempo_jira_mapping.columns.column_names import *


class CategoryMapper(TaskMapper):
    _WORK_COLUMN = CATEGORY_COLUMN_KEY
    _MAPPER_COLUMN = A1QA_CATEGORY_COLUMN_KEY
