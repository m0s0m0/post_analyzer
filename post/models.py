from django.db import models
import uuid


class Post(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    post_description = models.TextField(null=True)
    is_analysed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    analysed_at = models.DateTimeField(auto_now=True)
    total_words = models.IntegerField(default=0)
    average_word_length = models.FloatField(default=0.00)

    def __str__(self):
        return str(self.uuid)

    @property
    def analysis_response(self):
        return {
            'uid': self.uuid,
            'analysis': {
                'total_words': self.total_words,
                'average_word_length': self.average_word_length
            },
            'is_analysed': self.is_analysed
        }
