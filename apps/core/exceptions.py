from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """Custom DRF exception handler for standardized responses."""
    response = exception_handler(exc, context)

    if response is not None:
        data = response.data
        message = "Erro na requisição"
        code = exc.__class__.__name__

        if response.status_code == status.HTTP_404_NOT_FOUND:
            view = context.get("view")
            model_name = "Recurso"
            if view and hasattr(view, "get_queryset"):
                try:
                    model = view.get_queryset().model
                    model_name = str(model._meta.verbose_name).capitalize()
                except Exception:
                    pass
            message = f"{model_name} não encontrado(a)."
            code = "NotFound"
        elif isinstance(data, dict):
            if "detail" in data:
                message = data["detail"]
            else:
                errors = []
                for field, field_errors in data.items():
                    if isinstance(field_errors, list):
                        clean_errors = []
                        for e in field_errors:
                            err_str = str(e)
                            is_not_found = (
                                "não existe" in err_str.lower()
                                or "does not exist" in err_str.lower()
                            )
                            if is_not_found:
                                clean_errors.append("Objeto não encontrado.")
                            else:
                                clean_errors.append(err_str)
                        msg = " ".join(clean_errors)
                    else:
                        msg = str(field_errors)
                    errors.append(f"{field}: {msg}")
                message = "; ".join(errors) if errors else message
        elif isinstance(data, list):
            message = data[0] if data else message
        else:
            message = str(data)

        response.data = {"status": "error", "message": message, "code": code}
    else:
        return Response(
            {
                "status": "error",
                "message": "Ocorreu um erro interno no servidor.",
                "code": "InternalServerError",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response
