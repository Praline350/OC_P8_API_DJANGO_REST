from django.contrib import admin

from projects.models import Project, Contributor, Issue, Comment

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'created_time')


@admin.register(Contributor)
class ContributorAdmin(admin.ModelAdmin):
    list_display = ('user', 'project')


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('project', 'title', 'author', 'priority', 'created_time', 'updated_time')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('issue', 'author', 'created_time')
