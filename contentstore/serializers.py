from .models import Schedule, MessageSet

from rest_framework import serializers


class ScheduleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Schedule
        fields = ('id', 'minute', 'hour', 'day_of_week', 'day_of_month',
                  'month_of_year')


class MessageSetSerializer(serializers.ModelSerializer):

    class Meta:
        model = MessageSet
        fields = ('id', 'short_name', 'notes', 'next_set', 'default_schedule',
                  'created_at', 'updated_at')
