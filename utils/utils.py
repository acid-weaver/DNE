import json
from rest_framework.exceptions import ValidationError


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
            data = json.loads(self.data)
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
        raise ValidationError(f"{self.model.__name__}s provided with unsupported format. "
                              "Please use list of json or list of int "
                              f"with ID of {self.model.__name__}s.")
    

    def __call__(self):
        if self.logs:
            self.errors()
        self.parse_int()
        self.parse_dict()
        return self.instance
