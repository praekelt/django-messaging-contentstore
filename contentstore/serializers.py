from .models import Schedule

from rest_framework import serializers


class ScheduleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Schedule
        fields = ('id', 'minute', 'hour', 'day_of_week', 'day_of_month',
                  'month_of_year')
