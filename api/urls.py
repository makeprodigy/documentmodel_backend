from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet, QuestionViewSet, RegisterView
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'questions', QuestionViewSet, basename='question')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('', include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
