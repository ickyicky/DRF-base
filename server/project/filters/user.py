from django_filters import CharFilter, DateTimeFromToRangeFilter
from project.models.user import UserModel
from django_filters.rest_framework import FilterSet


class UserModelFilter(FilterSet):
    role = CharFilter(lookup_expr="icontains")
    modified_date = DateTimeFromToRangeFilter()

    class Meta:
        model = UserModel
        fields = ["role", "modified_date"]
