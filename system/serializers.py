from rest_framework import serializers
from system.models import BookInstance, BookStatus, Genre, Student
from django.db.models.functions import Concat
from django.db.models import Value

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'

class GenreListingField(serializers.RelatedField):
 
     def to_representation(self, value):
         return value.name


class BookInstanceSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='book.title')
    author = serializers.SerializerMethodField()
    genre = serializers.SerializerMethodField()#GenreSerializer(source="book.genre", many=True, read_only=True)
    publish_date = serializers.DateField(source='book.publish_date')
    status = serializers.SerializerMethodField()

    def get_author(self, instance):
        return ','.join(list(instance.book.author.annotate(
        full_name=Concat('first_name',
                         Value(' '),
                         'last_name')).values_list('full_name', flat=True)))

    def get_genre(self, instance):
        return ','.join(list(instance.book.genre.values_list('name', flat=True)))

    def get_status(self, instance):
        return BookStatus(instance.status).label

    class Meta:
        model = BookInstance
        # fields = '__all__'
        exclude = ('book',)
        depth = 1 