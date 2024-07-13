from rest_framework import serializers
from rest_framework.exceptions import ValidationError
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
    contributors = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        many=True,
        slug_field='username',
        required=False
    )

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'type', 'author', 'contributors', 'created_time']

    def create(self, validated_data):
        contributors_usernames = validated_data.pop('contributors', [])
        request = self.context.get('request')
        project = Project.objects.create(author=request.user, **validated_data)
        # Ajouter l'auteur comme contributeur
        Contributor.objects.create(user=request.user, project=project)
        
       # Ajouter les autres contributeurs en vérifiant les doublons
        for username in set(contributors_usernames):
            user = User.objects.get(username=username)
            if not Contributor.objects.filter(user=user, project=project).exists():
                Contributor.objects.create(user=user, project=project)
                
        return project
        


class ProjectDetailSerializer(ProjectListSerializer):
    class Meta(ProjectListSerializer.Meta):
        fields = ProjectListSerializer.Meta.fields

    def update(self, instance, validated_data):
        request = self.context.get('request')
        if instance.author != request.user:
            raise serializers.ValidationError("Vous n'avez pas les permissions")
        
        contributors_usernames = validated_data.pop('contributors', [])
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.type = validated_data.get('type', instance.type)
        instance.save()

        if contributors_usernames:
            new_contributors = set(contributors_usernames)
            new_contributors.add(request.user.username)
            current_contributors = set(instance.contributors.values_list('username', flat=True))
            contributors_to_add = new_contributors - current_contributors
            contributors_to_remove = current_contributors - new_contributors
            
            for username in contributors_to_add:
                user = User.objects.get(username=username)
                Contributor.objects.create(user=user, project=instance)
            
            for username in contributors_to_remove:
                user = User.objects.get(username=username)
                Contributor.objects.filter(user=user, project=instance).delete()
        
        return instance



class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.user.username')

    class Meta:
        model = Comment
        fields = ['id', 'issue', 'author', 'description', 'created_time']


class IssueListSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.user.username')
    project = serializers.ReadOnlyField(source='project.name')

    

    class Meta:
        model = Issue
        fields = ['id', 'project', 'author', 'title', 'description', 'status', 'priority', 'created_time', 'updated_time']
        read_only_fields = ['created_time', 'updated_time']


class IssueDetailSerializer(IssueListSerializer):
    class Meta(IssueListSerializer.Meta):
        fields = IssueListSerializer.fields 
