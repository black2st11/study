from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from proxy.models import ActivatedItem, DeletedItem, Item
from proxy.serializers import ActivatedItemSerializer, DeletedItemSerializer, ItemSerializer


class RecoverMixin:
    @action(methods=['POST'], detail=True)
    def recover(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        self.perform_recover(instance)
        return Response(status=status.HTTP_200_OK)

    @staticmethod
    def perform_recover(instance):
        instance.recover()


class ItemView(ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


class ActivatedItemView(ModelViewSet):
    queryset = ActivatedItem.objects.all()
    serializer_class = ActivatedItemSerializer


class DeletedItemView(RecoverMixin, ModelViewSet):
    queryset = DeletedItem.objects.all()
    serializer_class = DeletedItemSerializer

