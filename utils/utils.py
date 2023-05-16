import json
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer


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
        if not isinstance(self.data, str):
            return

        try:
            self.data = int(self.data)

        except ValueError:
            self.logs.append("_get_by_id_int to int conversion ValueError.")
            return
        
        self.instance = get_or_validation_error(self.data, self.model)

    def parse(self):
        if isinstance(self.data, dict):
            return 1
        elif isinstance(self.data, int):
            return 0

        try:
            self.data = dict(json.loads(self.data))

        except ValueError:
            self.logs.append("_get_by_id_dict to dict conversion ValueError. "
                             f"Data: {self.data}")
            return 0

        # except TypeError:
        #     self.logs.append("_get_by_id_dict to dict conversion TypeError. "
        #                      f"Data: {self.data}")
        #     return 0
        
        return 1

    def _get_by_id_dict(self):
        if not self.parse():
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

    def validate(self, serializer: ModelSerializer, context: dict) -> None:
        if not self.parse():
            raise ValidationError(f"{self.model.__name__}s provided with unsupported format.")

        if self.data.get('id', False):
            self._get_by_id_dict()

            # for case partial update
            data = serializer(self.instance).data
            data.update(self.data)

            # validation for existing instance
            self.serializer = serializer(self.instance, data=data, context=context)
            self.serializer.is_valid(raise_exception=True)

        else:
            # validation for new instance
            self.serializer = serializer(data=self.data, context=context)
            self.serializer.is_valid(raise_exception=True)

    def update(self):
        if not self.serializer:
            raise ValidationError(f"Run validation before update {self.model.__name__}.")

        self.instance = self.serializer.save()
        return self.instance
