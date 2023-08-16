from generate_customer_data_file.data.data_classes.brand_data_load import AGNDataLoad, ATIDataLoad, A1800DataLoad
from generate_customer_data_file.data.data_classes.general_data_load import GeneralDataLoad


class DataDescription:
    def __init__(self, brand_name, company_name, brand_code, warehouse_name, class_type) -> None:
        self.brand_name = brand_name
        self.company_name = company_name
        self.brand_code = brand_code
        self.warehouse_name = warehouse_name
        self.class_type = class_type

    def __repr__(self) -> str:
        return "DataDescription " + "\n".join([f"{k}: {v}" for k, v in self.__dict__.items()])

    def __str__(self) -> str:
        return self.__repr__()


brands = [{'brand_name': 'Take5 COSC', 'company_name': 'Take5 ', 'brand_code': '040', 'warehouse_name': 'BP040',
           'class_type': GeneralDataLoad},
          {'brand_name': 'Take5 FZ', 'company_name': 'Take5 ', 'brand_code': '055', 'warehouse_name': 'BP055',
           'class_type': GeneralDataLoad},
          {'brand_name': 'CarStar', 'company_name': 'CarStar', 'brand_code': '011', 'warehouse_name': 'BA011',
           'class_type': GeneralDataLoad},
          {'brand_name': 'Maaco', 'company_name': 'Maaco', 'brand_code': '022', 'warehouse_name': 'SP022',
           'class_type': GeneralDataLoad},
          {'brand_name': 'Fix Auto', 'company_name': 'Fix Auto', 'brand_code': '064', 'warehouse_name': 'AX064',
           'class_type': GeneralDataLoad},
          {'brand_name': 'ABRA', 'company_name': 'ABRA', 'brand_code': '021', 'warehouse_name': 'SP021',
           'class_type': GeneralDataLoad},
          {'brand_name': 'AGN', 'company_name': None, 'brand_code': None, 'warehouse_name': None,
           'class_type': AGNDataLoad},
          {'brand_name': 'ATI', 'company_name': None, 'brand_code': None, 'warehouse_name': None,
           'class_type': ATIDataLoad},
          {'brand_name': '1800', 'company_name': None, 'brand_code': None, 'warehouse_name': None,
           'class_type': A1800DataLoad}
          ]

brands = list(DataDescription(**i) for i in brands)
