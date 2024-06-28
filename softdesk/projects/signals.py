from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Comment, Issue

@receiver(post_save, sender=Comment)
def update_issue_updated_time(sender, instance, **kwargs):
    """Mise à jour auto du updated_time des issue quand un comment est posté"""
    
    issue = instance.issue
    issue.updated_time = timezone.now()
    issue.save()