from rest_framework_json_api import views


class ModelViewSet(views.ModelViewSet):
    def paginate_queryset(self, queryset, *args, **kwargs):
        if "no_page" in self.request.query_params:
            return None

        return super().paginate_queryset(queryset, *args, **kwargs)
