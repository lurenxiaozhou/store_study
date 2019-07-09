from rest_framework.routers import DefaultRouter

from . import views

urlpatterns = []

router = DefaultRouter()
router.register('areas',views.AreasViewSet,base_name='areas')
router.register(r'addresses', views.AddressViewSet, base_name='addresses')

urlpatterns += router.urls

