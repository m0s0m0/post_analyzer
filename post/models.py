from django.db import models
import uuid

class Post(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    post_description = models.TextField(null=True)
    is_analysed = models.BooleanField(default=False)
    analysis_response = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    analysed_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.uuid