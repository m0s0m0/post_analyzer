from rest_framework import serializers


class PostValidationSerializer(serializers.Serializer):
    uuid = serializers.CharField(min_length=1, max_length=200)
    post_description = serializers.CharField(min_length=1)
