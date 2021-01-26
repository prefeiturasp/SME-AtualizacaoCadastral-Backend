from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from ...models import RetornoMP
from ..serializers.retorno_mp_serializer import (RetornoMPSerializer, RetornoMPCreateSerializer)


class RetornoMPViewset(mixins.CreateModelMixin,
                       viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    lookup_field = 'uuid'
    queryset = RetornoMP.objects.all()
    serializer_class = RetornoMPSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return RetornoMPCreateSerializer
        return RetornoMPSerializer
