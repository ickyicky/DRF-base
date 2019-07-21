from rest_framework_json_api import views


class ModelViewSet(views.ModelViewSet):
    """
    Enchanced ModelViewSet, when no_query params is set, it doesnt paginate
    queryset and also you can define custom serializer classes for specific
    for ViewSet action. To set them, use serializer_classes variable, it has
    to be dict. Default value is taken from serializer_class variable.
    """
    serializer_classes = {}

    def paginate_queryset(self, queryset, *args, **kwargs):
        """
        If no_page param is set ViewSet uses no paginator.
        """
        if "no_page" in self.request.query_params:
            return None

        return super().paginate_queryset(queryset, *args, **kwargs)

    def get_serializer_class(self):
        """
        Returns serializer class depending on action.
        """
        return self.serializer_classes.get(self.action, self.serializer_class)
