from rest_framework.response import Response
from rest_framework import status
from .models import Image
from rest_framework import viewsets, permissions
from .serializers import ImageSerializer


class AvatarViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        user = self.request.user
        return Image.objects.filter(owner=user)
        



