from rest_framework import serializers
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from .models import Quiz, QuizQuestion
from dictionary.models import Word, Sentence
import random

# --- Quiz question serializer ---
class QuizQuestionSerializer(serializers.ModelSerializer):
    text = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = QuizQuestion
        fields = ['id', 'text', 'category', 'correct_answer', 'user_answer', 'is_correct', 'answered_at']

    def get_text(self, obj):
        return getattr(obj.content_object, "word", getattr(obj.content_object, "text", ""))

    def get_category(self, obj):
        return getattr(obj.content_object, "category", None)


# --- Quiz serializer ---
class QuizSerializer(serializers.ModelSerializer):
    questions = QuizQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'user', 'category', 'created_at', 'score', 'total_questions', 'success', 'questions']


# --- Create a quiz ---
class QuizCreateSerializer(serializers.Serializer):
    count = serializers.IntegerField(default=5)
    categories = serializers.ListField(child=serializers.CharField(), required=False)
    include_sentences = serializers.BooleanField(default=False)

    def create(self, validated_data):
        user = self.context['request'].user
        count = validated_data.get("count", 5)
        categories = validated_data.get("categories", [])
        include_sentences = validated_data.get("include_sentences", False)

        # Gather words
        words_qs = Word.objects.all()
        if categories:
            words_qs = words_qs.filter(category__name__in=categories)
        words = list(words_qs)

        # Gather sentences
        sentences = []
        if include_sentences:
            sentences_qs = Sentence.objects.all()
            sentences = list(sentences_qs)

        pool = words + sentences
        selected = random.sample(pool, min(count, len(pool)))

        # Create quiz
        quiz = Quiz.objects.create(user=user, total_questions=len(selected))

        for item in selected:
            if isinstance(item, Word):
                correct = {"spanish": item.translation}
                if item.category and item.category.name.lower() == "verb":
                    correct["conjugated_form"] = item.verb.conjugated_form if hasattr(item, "verb") else None
                ct = ContentType.objects.get_for_model(Word)
                QuizQuestion.objects.create(
                    quiz=quiz,
                    content_type=ct,
                    object_id=item.id,
                    correct_answer=correct
                )
            elif isinstance(item, Sentence):
                correct = {"spanish": item.translation}
                ct = ContentType.objects.get_for_model(Sentence)
                QuizQuestion.objects.create(
                    quiz=quiz,
                    content_type=ct,
                    object_id=item.id,
                    correct_answer=correct
                )

        return quiz


# --- Submit quiz answers ---
class QuizSubmitSerializer(serializers.Serializer):
    answers = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of answers with question_id and user_answer"
    )

    def update(self, instance, validated_data):
        answers = validated_data.get('answers', [])
        score = 0

        for ans in answers:
            question_id = ans.get("question_id")
            user_answer = ans.get("user_answer")
            try:
                question = instance.questions.get(id=question_id)
            except QuizQuestion.DoesNotExist:
                continue

            question.user_answer = user_answer
            question.answered_at = timezone.now()

            # Check correctness
            is_correct = True
            for key, value in question.correct_answer.items():
                if str(user_answer.get(key, "")).strip().lower() != str(value).strip().lower():
                    is_correct = False
                    break

            question.is_correct = is_correct
            if is_correct:
                score += 1
            question.save()

        instance.score = score
        instance.success = (score == instance.total_questions)
        instance.save()
        return instance