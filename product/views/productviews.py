from rest_framework import viewsets
from product.models.productmodel import Product
from product.serializers.productserializer import ProductSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated


class productViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer