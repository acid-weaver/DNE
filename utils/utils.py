import json
from rest_framework.exceptions import ValidationError


def get_or_validation_error(id:int, model, error_msg):
    try:
        return model.objects.get(id=id)
    except:
        raise ValidationError(error_msg)
    

class NestedModelHandler:
    def __init__(self, data, model):
        self.data = data
        self.model = model
        self.logs = []
        self.instance = None


    def _get_by_id_int(self):
        try:
            self.data = int(self.data)

        except ValueError:
            self.logs.append("_get_by_id_int to int conversion ValueError.")
            return
        
        self.instance = get_or_validation_error(self.data, self.model,
                            f"No {self.model.__name__} with ID {self.data}.")


    def _get_by_id_dict(self):
        try:
            self.data = dict(json.loads(self.data))

        except ValueError:
            self.logs.append("_get_by_id_dict to dict conversion ValueError.")
            return

        except TypeError:
            self.logs.append("_get_by_id_dict to dict conversion TypeError.")
            return

        id = self.data.get('id', None)
        if not id:
            raise ValidationError(f"Provided as dict {self.model.__name__} doesn't have an ID. ")

        self.instance = get_or_validation_error(id, self.model, 
                        f"Provided as dict {self.model.__name__} doesn't exist. ID {id}")


    def get_instance(self):
        self._get_by_id_int()
        self._get_by_id_dict()

        if not self.instance:
            self.error()

        return self.instance


    def update(self, serializer):
        self._get_by_id_dict()
        if not self.instance:
            self.error(_form_msg=1)

        data = serializer(self.instance).data
        data.update(self.data)
        serializer = serializer(self.instance, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()


    def error(self, _form_msg=2):
        error_msg = ''
        msg = [f"{self.model.__name__}s provided with unsupported format.",
               f"Please use list of json or list of int with ID of {self.model.__name__}s."]
        for i in range(_form_msg):
            error_msg += msg[i] + ' '

        raise ValidationError(error_msg)


    def __call__(self):
        if self.logs and not self.instance:
            self.error()
        return self.get_instance()
