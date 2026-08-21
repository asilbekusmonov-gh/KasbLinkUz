from django_filters import FilterSet, NumberFilter

from apps.models import WorkerProfile


class WorkerFilter(FilterSet):
    rating = NumberFilter(field_name="rating", lookup_expr="gte")
    user = NumberFilter(field_name="user__id", lookup_expr="exact")

    class Meta:
        model = WorkerProfile
        fields = ["worker_services__category", "service_districts", "user"]
