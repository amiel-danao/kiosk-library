from rest_framework import serializers
from system.models import BookInstance, BookStatus, Genre, Notification, OutgoingTransaction, Reservations, Student
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
    thumbnail = serializers.SerializerMethodField()

    def get_author(self, instance):
        return ','.join(list(instance.book.author.annotate(
        full_name=Concat('first_name',
                         Value(' '),
                         'last_name')).values_list('full_name', flat=True)))

    def get_genre(self, instance):
        return ','.join(list(instance.book.genre.values_list('name', flat=True)))

    def get_status(self, instance):
        return BookStatus(instance.status).label
    
    def get_thumbnail(self, instance):
        request = self.context.get('request')
        if instance.book.thumbnail and hasattr(instance.book.thumbnail, 'url'):
            photo_url = instance.book.thumbnail.url
            return request.build_absolute_uri(photo_url)
        else:
            return ''        

    class Meta:
        model = BookInstance
        # fields = '__all__'
        exclude = ('book',)
        depth = 1 

class OutgoingTransactionSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='book.book.title')
    
    class Meta:
        model = OutgoingTransaction
        fields = ('borrower', 'title', 'date_borrowed', 'return_date')

    
class ReservationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservations
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'