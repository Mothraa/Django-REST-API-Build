import django_filters
from .models import Issue, Comment


class IssueFilter(django_filters.FilterSet):
    project = django_filters.NumberFilter(field_name='project',  lookup_expr='exact')
    # priority = django_filters.ChoiceFilter(choices=Issue.Priority.choices())
    # tag = django_filters.ChoiceFilter(choices=Issue.Tag.choices())
    # status = django_filters.ChoiceFilter(choices=Issue.Status.choices())

    class Meta:
        model = Issue
        fields = ['project']  # , 'priority', 'tag', 'status']


class CommentFilter(django_filters.FilterSet):
    issue = django_filters.NumberFilter(field_name='issue', lookup_expr='exact')
    project = django_filters.NumberFilter(field_name='issue__project', lookup_expr='exact')

    class Meta:
        model = Comment
        fields = ['issue', 'project']
