from django.db.models import Q

from .models import Notificacao
from .utils import mercado_do_usuario                                   # 9.4


def notificacoes(request):
    # telas de login não têm usuário: não mostra nada
    if not request.user.is_authenticated:
        return {}

    mercado = mercado_do_usuario(request.user)                          # 9.4

    # do mercado do usuário e, dentro dele, para todos ou só para este usuário
    visiveis = Notificacao.objects.filter(mercado=mercado).filter(      # 9.4
        Q(destinatario__isnull=True) | Q(destinatario=request.user)
    )

    return {
        'notificacoes': visiveis[:10],
        'notificacoes_novas': visiveis.exclude(lida_por=request.user).count(),
    }