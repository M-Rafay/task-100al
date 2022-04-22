from rest_framework import serializers
from stock.models.stockmodel import Stock

class StockSerializer(serializers.ModelSerializer):
    """ Serializer for stock object """

    class Meta:
        model = Stock
        fields = '__all__'
        read_only_fields = ['id']

class ProductStockSerializer(serializers.ModelSerializer):
    """ Serializer for product-stock relation object """

    class Meta:
        model = Stock
        fields = '__all__'
        read_only_fields = ['id']
        depth = 1