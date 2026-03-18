from django.db.models import ProtectedError
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.viewsets import ModelViewSet

from .models import Professional
from .serializers import ProfessionalSerializer

_TAG = ["Profissionais"]


@extend_schema_view(
    list=extend_schema(summary="Listar profissionais", tags=_TAG),
    create=extend_schema(summary="Cadastrar profissional", tags=_TAG),
    retrieve=extend_schema(summary="Detalhar profissional", tags=_TAG),
    update=extend_schema(summary="Atualizar profissional (completo)", tags=_TAG),
    partial_update=extend_schema(summary="Atualizar profissional (parcial)", tags=_TAG),
    destroy=extend_schema(summary="Remover profissional", tags=_TAG),
)
class ProfessionalViewSet(ModelViewSet):
    queryset = Professional.objects.all()
    serializer_class = ProfessionalSerializer
    parser_classes = ModelViewSet.parser_classes + [FormParser, MultiPartParser]

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            from rest_framework.exceptions import ValidationError

            raise ValidationError(
                "Não é possível remover este profissional pois "
                "ele possui consultas agendadas."
            )
