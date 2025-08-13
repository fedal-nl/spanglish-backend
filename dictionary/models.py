from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class WordCategory(models.TextChoices):
    VERB = 'verb', 'Verb'
    NOUN = 'noun', 'Noun'
    ADJECTIVE = 'adj', 'Adjective'
    ADVERB = 'adv', 'Adverb'
    PRONOUN = 'pron', 'Pronoun'
    # Add other parts of speech as needed


class Word(models.Model):
    text = models.CharField(max_length=100)
    category = models.CharField(max_length=10, choices=WordCategory.choices)
    categories = models.ManyToManyField(Category, blank=True, related_name='words')

    def __str__(self):
        return self.text


class Verb(models.Model):
    word = models.OneToOneField(Word, on_delete=models.CASCADE, related_name='verb_info')

    def save(self, *args, **kwargs):
        if self.word.category != WordCategory.VERB:
            raise ValueError("Word must have category 'verb' to be linked to Verb model")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.word.text


class VerbTense(models.TextChoices):
    PRESENT = 'present', 'Present'
    PAST = 'past', 'Past'
    FUTURE = 'future', 'Future'
    PRETERITE = 'preterite', 'Preterite'
    IMPERFECT = 'imperfect', 'Imperfect'
    CONDITIONAL = 'conditional', 'Conditional'
    SUBJUNCTIVE = 'subjunctive', 'Subjunctive'
    # Add other Spanish tenses as needed


class VerbPerson(models.TextChoices):
    FIRST_SINGULAR = '1s', 'First Person Singular (yo)'
    SECOND_SINGULAR = '2s', 'Second Person Singular (tú)'
    THIRD_SINGULAR = '3s', 'Third Person Singular (él/ella/usted)'
    FIRST_PLURAL = '1p', 'First Person Plural (nosotros)'
    SECOND_PLURAL = '2p', 'Second Person Plural (vosotros)'
    THIRD_PLURAL = '3p', 'Third Person Plural (ellos/ellas/ustedes)'


class VerbConjugation(models.Model):
    verb = models.ForeignKey(Verb, on_delete=models.CASCADE, related_name='conjugations')
    tense = models.CharField(max_length=20, choices=VerbTense.choices)
    person = models.CharField(max_length=2, choices=VerbPerson.choices)
    conjugated_form = models.CharField(max_length=100)

    class Meta:
        unique_together = ('verb', 'tense', 'person')

    def __str__(self):
        return f"{self.verb.word.text} - {self.tense} - {self.person}: {self.conjugated_form}"


class Sentence(models.Model):
    text = models.TextField()
    related_words = models.ManyToManyField(Word, blank=True, related_name='sentences')

    def __str__(self):
        return self.text


class Translation(models.Model):
    language = models.CharField(max_length=10, default='en')  # e.g. 'en'
    text = models.CharField(max_length=255)

    # Generic relation to Word, Sentence, or future models
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"{self.text} ({self.language})"
