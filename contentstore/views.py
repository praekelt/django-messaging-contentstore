from .models import Schedule, MessageSet
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .serializers import ScheduleSerializer, MessageSetSerializer


class ScheduleViewSet(ModelViewSet):

    """
    API endpoint that allows Schedule models to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer


class MessageSetViewSet(ModelViewSet):

    """
    API endpoint that allows MessageSet models to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    queryset = MessageSet.objects.all()
    serializer_class = MessageSetSerializer
