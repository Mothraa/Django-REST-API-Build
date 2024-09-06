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
            age=validated_data['age'],
        )
        return user


class CustomUserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        # fields = '__all__' => pb affiche même le mdp
        fields = ['id', 'username', 'age', 'can_be_contacted', 'can_data_be_shared', 'is_active', 'created_at']


class CustomUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'age', 'can_be_contacted', 'can_data_be_shared']


class TokenBlacklistSerializer(serializers.Serializer):
    refresh = serializers.CharField()


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
    # project_details = ProjectSerializer(source='project', read_only=True)

    class Meta:
        model = Issue
        fields = ['id', 'title', 'project', 'description', 'assignee',
                  'priority', 'tag', 'status', 'author', 'created_time']
        read_only_fields = ['author', 'created_time']


class CommentSerializer(serializers.ModelSerializer):
    # ajout du projet via une methode (champ non présent dans le model)
    project = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'description', 'issue', 'project', 'author', 'created_time']
        read_only_fields = ['id', 'issue', 'author', 'created_time']

    def get_project(self, obj):
        return {
            "id": obj.issue.project.id,
            "name": obj.issue.project.name,
            "description": obj.issue.project.description
        }

    def validate(self, data):
        # Dans le cas d'une mise à jour, pour remonter une exception sur la modif de l'ID issue
        # (le read_only_fields ne le fait pas tout seul)
        print(data)
        if 'issue' in data:
            raise CustomBadRequest("Le changement d'ID de l'Issue n'est pas authorisé")

        return data
