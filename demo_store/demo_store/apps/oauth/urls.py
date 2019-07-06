from django.conf.urls import url,include
from . import views


urlpatterns=[
    url(r'^qq/authorization/$',views.QQAuthURLView.as_view())
]