from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Quiz
from .serializers import QuizSerializer, QuizCreateSerializer, QuizSubmitSerializer

class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def create_quiz(self, request):
        serializer = QuizCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        quiz = serializer.save()
        return Response(QuizSerializer(quiz).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        quiz = self.get_object()
        serializer = QuizSubmitSerializer(instance=quiz, data=request.data)
        serializer.is_valid(raise_exception=True)
        quiz = serializer.save()
        return Response(QuizSerializer(quiz).data)
