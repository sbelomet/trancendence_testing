# upload/serializers.py
from rest_framework import serializers
from .models import Image

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'name', 'file', 'owner', 'date']
        read_only_fields = ['id', 'owner', 'date']
