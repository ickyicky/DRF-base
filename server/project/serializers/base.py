from rest_framework.serializers import ModelSerializer as BaseModelSerializer

from rest_framework_json_api import serializers


class ModelSerializer(BaseModelSerializer):
    id = serializers.IntegerField(
        read_only=False, required=False
    )  # so we parse id as we update

    def create(self, validated_data):
        validated_data.pop("id", None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("id", None)
        return super().update(instance, validated_data)


class PartialUpdateModelSerializer(ModelSerializer):
    # Please, do include extra_kwargs in Meta class like this:
    #     'role': {'required': False,}
    def update(self, instance, validated_data):
        validated_data.pop("id", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
