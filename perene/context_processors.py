from django.db.models import Q

from .models import Notificacao


def notificacoes(request):
    # telas de login não têm usuário: não mostra nada
    if not request.user.is_authenticated:
        return {}

    # notificações para todos (sem destinatário) ou só para este usuário
    visiveis = Notificacao.objects.filter(
        Q(destinatario__isnull=True) | Q(destinatario=request.user)
    )

    return {
        'notificacoes': visiveis[:10],
        'notificacoes_novas': visiveis.exclude(lida_por=request.user).count(),
    }