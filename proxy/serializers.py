from rest_framework import serializers

from proxy.models import ActivatedItem, DeletedItem, Item


class ActivatedItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = ActivatedItem
        fields = "__all__"


class DeletedItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeletedItem
        fields = "__all__"


class ItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = Item
        fields = "__all__"
