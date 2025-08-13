from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import Word, Verb, Sentence, Translation, Category, WordCategory, VerbConjugation

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


# --- Verb with nested conjugations ---
class VerbConjugationSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerbConjugation
        fields = ['id', 'tense', 'person', 'conjugated_form']


class VerbSerializer(serializers.ModelSerializer):
    """
    Read/Write serializer that supports nested conjugations.
    POST/PUT/PATCH payload includes `word` (pk) and `conjugations`: [{tense, person, conjugated_form}, ...]
    """
    conjugations = VerbConjugationSerializer(many=True)

    class Meta:
        model = Verb
        fields = ['id', 'word', 'conjugations']

    def validate(self, attrs):
        word = attrs.get('word') or getattr(self.instance, 'word', None)
        if not word:
            raise serializers.ValidationError({"word": "This field is required."})
        if word.category != WordCategory.VERB:
            raise serializers.ValidationError({"word": "Linked Word must have category 'verb'."})
        return attrs

    def create(self, validated_data):
        conj_data = validated_data.pop('conjugations', [])
        verb = Verb.objects.create(**validated_data)
        # Create conjugations
        for c in conj_data:
            VerbConjugation.objects.create(verb=verb, **c)
        return verb

    def update(self, instance, validated_data):
        conj_data = validated_data.pop('conjugations', None)

        # update the simple fields (word generally won’t change, but allow it)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()

        # If conjugations provided, replace them (simple, reliable strategy)
        if conj_data is not None:
            instance.conjugations.all().delete()
            for c in conj_data:
                VerbConjugation.objects.create(verb=instance, **c)

        return instance

class SentenceSerializer(serializers.ModelSerializer):
    translations = serializers.SerializerMethodField()

    class Meta:
        model = Sentence
        fields = '__all__'

    def get_translations(self, obj):
        ct = ContentType.objects.get_for_model(Sentence)
        translations = Translation.objects.filter(content_type=ct, object_id=obj.id)
        return TranslationSerializer(translations, many=True).data
    