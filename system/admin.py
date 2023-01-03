from django.contrib import admin
from django.apps import apps
from django.contrib.auth.models import Group
from system.models import Book

admin.site.unregister(Group)
exempted_models = (Group, )


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    fields = ('isbn', 'title', 'genre', 'author', )
    list_display = ('isbn', 'title','genres', 'authors',
                    'classification_number', 'publish_date')
    list_filter = ('isbn',
                   'classification', 'publish_date')
    search_fields = ('isbn', 'title',
                     'classification', 'publish_date')

    def authors(self, obj):
        return ",".join([str(p) for p in obj.author.all()])

    def genres(self, obj):
        return ",".join([str(p) for p in obj.genre.all()])

    def classification_number(self, obj):
        return str(obj.classification).zfill(3)


app_config = apps.get_app_config('system')
models = app_config.get_models()

for model in models:
    if model.__class__ in exempted_models:
        continue
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass

admin.site.site_header = "Kiosk Book Library"
admin.site.site_title = 'NCST Kiosk Book Library System'
admin.site.index_title = "Welcome to Kiosk Book Library"
