from rest_framework import viewsets
from stock.models.stockmodel import Stock
from stock.serializers.stockserializer import StockSerializer, ProductStockSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated


class stockViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]    
    queryset = Stock.objects.all()
    serializer_class = StockSerializer


class stockViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Stock.objects.all()
    serializer_class = ProductStockSerializer