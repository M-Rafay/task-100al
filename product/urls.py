from django.urls import path, include
from rest_framework import routers
from product.views.productviews import productViewSet


app_name = 'product'

router = routers.SimpleRouter()
router.register(r'products', productViewSet)
urlpatterns = [
    path('', include(router.urls)),
]

# router = routers.DefaultRouter()
# router.register(r'products', productViewSet)
# urlpatterns= [
#     # path('', productViewSet.as_view({
#     # 'get': 'retrieve',
#     # 'put': 'update',
#     # 'patch': 'partial_update',
#     # 'delete': 'destroy'
#     # })
#     # , name='products'),
# ]