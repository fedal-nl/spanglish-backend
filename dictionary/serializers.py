from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import Word, Verb, Sentence, Translation, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class TranslationSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField()

    class Meta:
        model = Translation
        fields = ['id', 'language', 'text', 'content_type', 'object_id']

    def to_representation(self, instance):
        """Show content_type as model name instead of ID."""
        rep = super().to_representation(instance)
        rep['content_type'] = instance.content_type.model
        return rep

    def validate_content_type(self, value):
        """Convert model name to ContentType object."""
        try:
            ct = ContentType.objects.get(model=value.lower())
            return ct
        except ContentType.DoesNotExist:
            raise serializers.ValidationError(f"Invalid content type: {value}")

    def create(self, validated_data):
        validated_data['content_type'] = validated_data['content_type']
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['content_type'] = validated_data['content_type']
        return super().update(instance, validated_data)


class WordSerializer(serializers.ModelSerializer):
    translations = serializers.SerializerMethodField()

    class Meta:
        model = Word
        fields = '__all__'

    def get_translations(self, obj):
        ct = ContentType.objects.get_for_model(Word)
        translations = Translation.objects.filter(content_type=ct, object_id=obj.id)
        return TranslationSerializer(translations, many=True).data


class VerbSerializer(serializers.ModelSerializer):
    translations = serializers.SerializerMethodField()

    class Meta:
        model = Verb
        fields = '__all__'

    def get_translations(self, obj):
        ct = ContentType.objects.get_for_model(Verb)
        translations = Translation.objects.filter(content_type=ct, object_id=obj.id)
        return TranslationSerializer(translations, many=True).data


class SentenceSerializer(serializers.ModelSerializer):
    translations = serializers.SerializerMethodField()

    class Meta:
        model = Sentence
        fields = '__all__'

    def get_translations(self, obj):
        ct = ContentType.objects.get_for_model(Sentence)
        translations = Translation.objects.filter(content_type=ct, object_id=obj.id)
        return TranslationSerializer(translations, many=True).data
    