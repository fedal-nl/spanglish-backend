from django.contrib import admin
from .models import Word, Sentence, Translation, Verb, VerbConjugation, Category
from django.contrib.contenttypes.admin import GenericTabularInline

class TranslationInline(GenericTabularInline):
    model = Translation
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('text', 'category')
    list_filter = ('category',)
    search_fields = ('text',)

    inlines = [TranslationInline]

@admin.register(Sentence)
class SentenceAdmin(admin.ModelAdmin):
    list_display = ('text',)
    search_fields = ('text',)

@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    list_display = ('get_related_object', 'text', 'language')
    list_filter = ('language',)
    search_fields = ('text', 'text')

    def get_related_object(self, obj):
        return str(obj.content_object)  # calls __str__ of the related object
    
    get_related_object.short_description = 'Word/Sentence'

@admin.register(Verb)
class VerbAdmin(admin.ModelAdmin):
    list_display = ('word',)
    search_fields = ('word',)

@admin.register(VerbConjugation)
class ConjunctionAdmin(admin.ModelAdmin):
    list_display = ('verb', 'tense', 'person', 'conjugated_form')
    search_fields = ('verb',)
