import json
from rest_framework.exceptions import ValidationError


def safe_converter(data, to_type:type, logs:list=[], value_error:str="ValueError"):
    """
    Converts data to provided class.
    All needed for to_type(data) line methods must be implemented.

    :param data: Data what needed to be converted.
    :param type to_type: To which format data must be converted.

    :param list logs: List what would be extended with error messages, 
    defaults to []
    :param str value_error: Logs would be extended with this message 
    in case of ValueError, defaults to "ValueError"

    :return to_type or None: Returns data in "to_type" format. 
    If error occured returns None.
    """
    try:
        data = to_type(data)
        return(data)
    except ValueError:
        logs.append(value_error)


def get_or_validation_error(id:int, model, error_msg):
    try:
        return model.objects.get(id=id)
    except:
        raise ValidationError(error_msg)
    

class ModelRequestValidator:
    def __init__(self, data, model, **kwargs):
        self.data = data
        self.model = model
        self.logs = []
        self.instance = None
        self._options = kwargs


    def parse_int(self):
        try:
            id = int(self.data)
            self.instance = get_or_validation_error(id, self.model,
                               f"No {self.model.__name__} with ID {id}.")

        except ValueError:
            self.logs.append('ValueError')


    def parse_dict(self):
        try:
            # print(self.data)
            data = json.loads(self.data)
            # print(data)
            id = data.get('id', None)

            if not id:
                raise ValidationError(f"Provided as dict {self.model.__name__} doesn't have an ID. ")

            self.instance = get_or_validation_error(id, self.model, 
                            f"Provided as dict {self.model.__name__} doesn't exist. ID {id}")

        except ValueError:
            self.logs.append(f"ValueError with data {self.data}")
        except TypeError:
            self.logs.append(f"TypeError with data {self.data}")
        except AttributeError:
            self.logs.append(f"AttributeError with data {self.data}")

    def errors(self):
        # print(self.logs)
        raise ValidationError(f"{self.model.__name__}s provided with unsupported format. "
                              "Please use list of json or list of int "
                              f"with ID of {self.model.__name__}s.")
    

    def __call__(self):
        if self.logs:
            self.errors()
        self.parse_int()
        self.parse_dict()
        return self.instance
