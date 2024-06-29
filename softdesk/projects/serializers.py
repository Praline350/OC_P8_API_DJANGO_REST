from rest_framework import serializers
from django.contrib.auth import get_user_model

from projects.models import Project, Contributor, Issue, Comment

User = get_user_model()


class ContributorSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    project = serializers.StringRelatedField()

    class Meta:
        model = Contributor
        fields = ['user', 'project']


class ProjectListSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    contributors = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, required=False)

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'type', 'author', 'contributors', 'created_time']

    def create(self, validated_data):
        contributors_data = validated_data.pop('contributors', [])
        request = self.context.get('request')
        project = Project.objects.create(author=request.user, **validated_data)
        # Ajouter l'auteur comme contributeur et supprimer les doublons
        unique_contributors = set(contributors_data)
        unique_contributors.add(project.author)
        for user in unique_contributors:
            Contributor.objects.create(user=user, project=project)
        return project
    

class ProjectDetailSerializer(ProjectListSerializer):
    class Meta(ProjectListSerializer.Meta):
        fields = ProjectListSerializer.Meta.fields

    def update(self, instance, validated_data):
        request = self.context.get('request')
        if instance.author != request.user:
            raise serializers.ValidationError("Vous n'avez pas les permissions")
        contributors_data = validated_data.pop('contributors', [])
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.type = validated_data.get('type', instance.type)
        instance.save()
        if contributors_data is not None:
            new_contributors = set([user.id for user in contributors_data])
            new_contributors.add(request.user.id)
            current_contributors = set(instance.contributors.values_list('id', flat=True))
            contributors_to_add = new_contributors - current_contributors
            contributors_to_remove = current_contributors - new_contributors
            for user_id in contributors_to_add:
                user = User.objects.get(id=user_id)
                Contributor.objects.create(user=user, project=instance)
            for user_id in contributors_to_remove:
                Contributor.objects.filter(user_id=user_id, project=instance).delete()
            return instance

