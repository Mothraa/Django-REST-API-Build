from rest_framework import serializers
from .models import CustomUser, Project, Contributor, Issue, Comment
from .exceptions import CustomBadRequest


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'password', 'age', 'is_superuser']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            age=validated_data['age']
        )
        return user


class CustomUserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        # fields = '__all__'
        fields = ['id', 'username', 'age', 'can_be_contacted', 'can_data_be_shared', 'is_active', 'created_at']


class CustomUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'age', 'can_be_contacted', 'can_data_be_shared']


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'type', 'author', 'created_time']
        read_only_fields = ['author', 'created_time']


class ContributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contributor
        fields = ['user', 'project']


class IssueSerializer(serializers.ModelSerializer):
    # TODO : passer les validations d'ID de la vue au serializer, exemple :
    # def validate(self, data):
    #     project_id = data.get('project')
    #     if project_id and not Project.objects.filter(pk=project_id).exists():
    #         raise serializers.ValidationError({'project': 'Le projet spécifié n\'existe pas.'})

    class Meta:
        model = Issue
        fields = ['id', 'title', 'description', 'project', 'assignee',
                  'priority', 'tag', 'status', 'author', 'created_time']
        read_only_fields = ['project', 'author', 'created_time']

    def validate(self, data):
        # Dans le cas d'une mise à jour, pour remonter une exception sur la modif de l'ID project
        # (le read_only_fields ne le fait pas tout seul)
        if self.instance:
            current_project_id = self.instance.project.id
            new_project_id = data.get('project')

            # on ne peut pas modifier l'ID de rattachement de l'Issue au Projet
            if new_project_id and new_project_id != current_project_id:
                raise CustomBadRequest("Le changement de l'ID du Projet n'est pas authorisé")
        return data
    # TODO : ajouter des validate pour author et created_time sur le même principe que project


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'description', 'issue', 'author', 'created_time']
        read_only_fields = ['issue', 'author', 'created_time']

    def validate(self, data):
        # Dans le cas d'une mise à jour, pour remonter une exception sur la modif de l'ID issue
        # (le read_only_fields ne le fait pas tout seul)
        if self.instance:
            current_issue_id = self.instance.issue.id
            new_issue_id = data.get('issue')

            # on ne peut pas modifier l'ID de rattachement du commentaire a l'Issue
            if new_issue_id and new_issue_id != current_issue_id:
                raise CustomBadRequest("Le changement de l'ID de l'Issue n'est pas authorisé")
        return data

    # TODO : ajouter des validate pour author et created_time sur le même principe que issue
