from django.contrib import admin
import datetime
from django.utils import timezone
from django.utils.timezone import get_current_timezone


OPENING_HOUR = 9
CLOSING_HOUR = 17
SCHEDULE_DATEFORMAT = "%Y-%m-%d, %I:%M %p"
SCHEDULE_DATEFORMAT_24H = "%Y-%m-%d, %H:%M"


def global_context(request):
    return {
        'app_title': admin.site.site_title,
        'app_short_title': 'Kiosk Book Library',
        'app_description': 'NCST Kiosk Book Library System',
        'app_schedule': 'Mon - Fri : 09.00 AM - 05.00 PM',
        'app_location': '',
        'app_contact_no': '0995-473-4825',
        'today': get_correct_today(),
        'min_time': get_correct_today(format='%I:%M')
    }


def get_correct_today(date=None, format=SCHEDULE_DATEFORMAT):
    if date is None:
        date = timezone.localtime()  # datetime.datetime.now(tz=get_current_timezone())
    hour = max(OPENING_HOUR, date.hour)

    minute = round(date.minute/30.0) * 30
    if minute == 60:
        minute = 0
        hour += 1

    if hour > CLOSING_HOUR:
        date = date + datetime.timedelta(days=1)
        minute = 0
        hour = OPENING_HOUR

    date = datetime.datetime(date.year, date.month,
                             date.day, hour, minute, tzinfo=get_current_timezone())

    return date.strftime(format)
