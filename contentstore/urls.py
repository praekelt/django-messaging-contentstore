from django.conf.urls import url, include
from rest_framework import routers
import views

router = routers.DefaultRouter()
router.register(r'schedule', views.ScheduleViewSet)
router.register(r'messageset', views.MessageSetViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/',
        include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth/',
        'rest_framework.authtoken.views.obtain_auth_token')
]
