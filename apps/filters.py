from django_filters import NumberFilter, FilterSet

from apps.models import WorkerProfile


class WorkerFilter(FilterSet):
    rating = NumberFilter(field_name='rating', lookup_expr='gte')

    class Meta:
        model = WorkerProfile
        fields = ['worker_services__category', 'city']
