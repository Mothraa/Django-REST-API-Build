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
        fields = ['id', 'title', 'project', 'description', 'assignee',
                  'priority', 'tag', 'status', 'author', 'created_time']
        read_only_fields = ['project', 'author', 'created_time']

    # def validate(self, data):
    #     # pour remonter une exception sur la modif de l'ID project
    #     # (le read_only_fields ne le fait pas tout seul)
    #     print(data)
    #     project_id = self._get_project_id(data)
    #     print(f"project_id : {project_id}")
    #     print(self.instance)
    #     if self.instance:
    #         print("update instance")
    #         self._validate_update(data, project_id)
    #     else:
    #         self._validate_create(data, project_id)
    #     return data

    # def _validate_create(self, data, project_id):
    #     """
    #     Validate data for a creation
    #     """
    #     # Vérifie que l'ID du projet est spécifié
    #     project_id = data.get('project')
    #     if not project_id:
    #         raise CustomBadRequest("Le projet doit être spécifié")

    #     # Validation pour l'assigné
    #     # self._validate_assignate(data, project_id)

    # def _validate_update(self, data, project_id):
    #     """
    #     Validate data for an update
    #     """
    #     # Obtenir l'ID du projet actuel depuis l'instance
    #     current_project_id = self.instance.project.id
    #     print(current_project_id)
    #     print(project_id)
    #     # Vérifie que l'ID du projet n'a pas été modifié
    #     if project_id and project_id != current_project_id:
    #         print("condition ok")
    #         raise CustomBadRequest("Le changement de l'ID du Projet n'est pas autorisé")

        # Vérifie que les champs en lecture seule ne sont pas modifiés
        # self._check_read_only_fields(data)

        # self._validate_assignate(data, current_project_id)

    def _get_project_id(self, data):
        """
        Return project ID whatever a creation or an update
        """
        if self.instance:  # maj
            return self.instance.project.id
        else:  # creation
            # print(data)

            return data.get('project')
            # return self.context['request'].data.get('project')

    # def _validate_assignate(self, data, project_id):
    #     """
    #     Validate if an assignated user is a project contributor
    #     """
    #     new_assignee_id = data.get('assignee')
    #     if new_assignee_id and not Contributor.objects.filter(project_id=project_id, user_id=new_assignee_id).exists():
    #         raise CustomBadRequest("L'utilisateur assigné ne fait pas partie des contributeurs du projet")

    # def _check_read_only_fields(self, data):
    #     """
    #     Add an exception if try to add/update readonly fields + parent ID (projects)
    #     """
    #     for field in ['author', 'created_time']:  #'project', 
    #         if field in data:
    #             raise CustomBadRequest(f"Vous ne pouvez pas changer le champ '{field}'")


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
