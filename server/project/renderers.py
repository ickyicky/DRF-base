from collections import OrderedDict

from django.utils import six
from rest_framework import relations
from rest_framework.serializers import BaseSerializer

from rest_framework_json_api import utils
from rest_framework_json_api.renderers import JSONRenderer


class BetterJSONRenderer(JSONRenderer):
    @classmethod
    def extract_attributes(cls, fields, resource):
        """
        Builds the `attributes` object of the JSON API resource object.
        Behaves better than default when serializing nested models.
        """
        data = OrderedDict()
        for field_name, field in six.iteritems(fields):
            # ID is always provided in the root of JSON API so remove it from attributes
            if field_name == "id":
                continue
            # don't output a key for write only fields
            if fields[field_name].write_only:
                continue

            # Skip read_only attribute fields when `resource` is an empty
            # serializer. Prevents the "Raw Data" form of the browsable API
            # from rendering `"foo": null` for read only fields.
            # Also we dont want to see None nested serializer objects.
            try:
                resource[field_name]
            except KeyError:
                if fields[field_name].read_only or isinstance(
                    field,
                    (
                        relations.RelatedField,
                        relations.ManyRelatedField,
                        BaseSerializer,
                    ),
                ):
                    continue

            data.update({field_name: resource.get(field_name)})

        return utils._format_object(data)  # pylint: disable=W0212
