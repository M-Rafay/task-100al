from django.urls import path, include
from rest_framework import routers
from stock.views.stockviews import stockViewSet


app_name = 'stock'

router = routers.SimpleRouter()
router.register(r'stocks', stockViewSet)
router.register(r'product-stocks', stockViewSet)
urlpatterns= [
    path('', include(router.urls)),
]