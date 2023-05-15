import json
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError


def get_or_validation_error(id:int, model):
    try:
        return model.objects.get(id=id)
    except ObjectDoesNotExist:
        raise ValidationError(f"No {model.__name__} with ID {id}.")


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
        
        self.instance = get_or_validation_error(self.data, self.model)


    def _get_by_id_dict(self):
        try:
            self.data = dict(json.loads(self.data))

        except ValueError:
            self.logs.append("_get_by_id_dict to dict conversion ValueError. "
                             f"Data: {self.data}")
            return

        except TypeError:
            self.logs.append("_get_by_id_dict to dict conversion TypeError. "
                             f"Data: {self.data}")
            return

        id = self.data.get('id', None)
        if not id:
            raise ValidationError(f"Provided as dict {self.model.__name__} doesn't have an ID. ")

        self.instance = get_or_validation_error(id, self.model)


    def get_instance(self):
        self._get_by_id_int()
        self._get_by_id_dict()

        if not self.instance:
            raise ValidationError(f"{self.model.__name__}s provided with unsupported format."
                                  f"Please use list of json or list of int with ID of {self.model.__name__}s.")

        return self.instance


    def update(self, serializer):
        self._get_by_id_dict()

        if not self.instance and not isinstance(self.data, dict):
            print(self.logs)
            raise ValidationError(f"{self.model.__name__}s provided with unsupported format.")

        if self.instance:
            data = serializer(self.instance).data
            data.update(self.data)
            serializer = serializer(self.instance, data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        else:
            serializer = serializer(data=self.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()


    def __call__(self):
        if self.logs and not self.instance:
            raise ValidationError(f"{self.model.__name__}s provided with unsupported format."
                                  f"Logs: {self.logs}")
        return self.get_instance()
