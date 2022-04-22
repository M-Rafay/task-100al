from rest_framework import serializers
from product.models.productmodel import Product

class ProductSerializer(serializers.ModelSerializer):
    """ Serializer for product object """

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['id']
        depth = 1

# class ProductSerializer(serializers.ModelSerializer):
#     """ Serializer for product object """

#     class Meta:
#         model = Product
#         fields = '__all__'
#         read_only_fields = ['id']
#         depth = 1
