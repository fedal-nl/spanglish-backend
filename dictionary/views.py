from rest_framework import viewsets
from .models import Word, Verb, Sentence, Translation, Category
from django.contrib.contenttypes.models import ContentType
from .serializers import WordSerializer, VerbSerializer, SentenceSerializer, TranslationSerializer, CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class WordViewSet(viewsets.ModelViewSet):
    queryset = Word.objects.all()
    serializer_class = WordSerializer

class VerbViewSet(viewsets.ModelViewSet):
    queryset = Verb.objects.all()
    serializer_class = VerbSerializer

class SentenceViewSet(viewsets.ModelViewSet):
    queryset = Sentence.objects.all()
    serializer_class = SentenceSerializer

class TranslationViewSet(viewsets.ModelViewSet):
    queryset = Translation.objects.all()
    serializer_class = TranslationSerializer

    def get_queryset(self):
            queryset = super().get_queryset()
            content_type_param = self.request.query_params.get("content_type")
            object_id_param = self.request.query_params.get("object_id")

            if content_type_param and object_id_param:
                try:
                    # Match content type from model name
                    content_type = ContentType.objects.get(model=content_type_param.lower())
                    queryset = queryset.filter(
                        content_type=content_type,
                        object_id=object_id_param
                    )
                except ContentType.DoesNotExist:
                    queryset = queryset.none()

            return queryset