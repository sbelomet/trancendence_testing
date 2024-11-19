from django.urls import path, include
from rest_framework import routers
from .views import AvatarViewSet
from django.conf import settings
from django.conf.urls.static import static

router = routers.DefaultRouter()
router.register(r'avatar', AvatarViewSet, basename='avatar')

urlpatterns = [
    path('', include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#cet ajout + est uniquement pour le dev!!