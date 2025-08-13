from rest_framework.routers import DefaultRouter
from .views import WordViewSet, VerbViewSet, SentenceViewSet, TranslationViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'words', WordViewSet)
router.register(r'verbs', VerbViewSet)
router.register(r'sentences', SentenceViewSet)
router.register(r'translations', TranslationViewSet)

urlpatterns = router.urls
