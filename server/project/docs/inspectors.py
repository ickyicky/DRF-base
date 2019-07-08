from collections import OrderedDict

from drf_yasg import openapi
from drf_yasg.inspectors import NotHandled, FieldInspector
from rest_framework_json_api import serializers
from rest_framework_json_api.utils import (
    get_related_resource_type,
    get_resource_type_from_serializer,
)


class ResourceRelatedFieldInspector(FieldInspector):
    def field_to_swagger_object(
        self, field, swagger_object_type, use_references, **kwargs
    ):
        if isinstance(field, serializers.ResourceRelatedField):
            return None

        return NotHandled


class ModelSerializerInspector(FieldInspector):
    def process_result(self, result, method_name, obj, **kwargs):
        if (
            isinstance(obj, serializers.ModelSerializer)
            and method_name == "field_to_swagger_object"
        ):
            model_response = self.formatted_model_result(result, obj)
            if obj.parent is None and self.view.action != "list":
                return self.decorate_with_data(model_response)

            return model_response

        return result

    def generate_relationships(self, obj):
        relationships_properties = []
        for field in obj.fields.values():
            if isinstance(field, serializers.ResourceRelatedField):
                relationships_properties.append(self.generate_relationship(field))
        if relationships_properties:
            return openapi.Schema(
                title="Relationships of object",
                type=openapi.TYPE_OBJECT,
                properties=OrderedDict(relationships_properties),
            )

        return None

    def generate_relationship(self, field):
        field_schema = openapi.Schema(
            title="Relationship object",
            type=openapi.TYPE_OBJECT,
            properties=OrderedDict(
                (
                    (
                        "type",
                        openapi.Schema(
                            type=openapi.TYPE_STRING,
                            title="Type of related object",
                            enum=[get_related_resource_type(field)],
                        ),
                    ),
                    (
                        "id",
                        openapi.Schema(
                            type=openapi.TYPE_STRING, title="ID of related object"
                        ),
                    ),
                )
            ),
        )
        return field.field_name, self.decorate_with_data(field_schema)

    def formatted_model_result(self, result, obj):
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["properties"],
            properties=OrderedDict(
                (
                    (
                        "type",
                        openapi.Schema(
                            type=openapi.TYPE_STRING,
                            enum=[get_resource_type_from_serializer(obj)],
                            title="Type of related object",
                        ),
                    ),
                    (
                        "id",
                        openapi.Schema(
                            type=openapi.TYPE_STRING,
                            title="ID of related object",
                            read_only=True,
                        ),
                    ),
                    ("attributes", result),
                    ("relationships", self.generate_relationships(obj)),
                )
            ),
        )

    def decorate_with_data(self, result):
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["data"],
            properties=OrderedDict((("data", result),)),
        )
