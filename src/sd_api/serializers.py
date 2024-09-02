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
    class Meta:
        model = Issue
        fields = ['id', 'title', 'project', 'description', 'assignee',
                  'priority', 'tag', 'status', 'author', 'created_time']
        read_only_fields = ['project', 'author', 'created_time']

    def _get_project_id(self, data):
        """
        Return project ID whatever a creation or an update
        """
        if self.instance:  # maj
            return self.instance.project.id
        else:  # creation
            # print(data)

            return data.get('project')


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'description', 'issue', 'author', 'created_time']
        read_only_fields = ['author', 'created_time']

    def validate(self, data):
        # Dans le cas d'une mise à jour, pour remonter une exception sur la modif de l'ID issue
        # (le read_only_fields ne le fait pas tout seul)
        if self.instance:
            current_issue_id = self.instance.issue.id
            new_issue_id = data.get('issue')

            # on ne peut pas modifier l'ID de rattachement du commentaire a l'Issue
            if new_issue_id and new_issue_id != current_issue_id:
                raise CustomBadRequest("Le changement de l'ID de l'Issue n'est pas authorisé")

        self._check_read_only_fields(data)

        return data

    def _check_read_only_fields(self, data):
        """
        Add an exception if try to add/update readonly fields + parent ID (Issue)
        """
        # TODO list a ajouter en param
        for field in ['issue', 'author', 'created_time']:
            if field in data:
                raise CustomBadRequest(f"Vous ne pouvez pas changer le champ '{field}'.")
