from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def eh_gestor(user):
    """True se o usuário tem perfil de gestor."""
    perfil = getattr(user, 'perfil', None)
    return perfil is not None and perfil.papel == 'gestor'


def gestor_required(view):
    """Deixa passar só gestores. Os outros voltam para o estoque com um aviso."""
    @wraps(view)
    @login_required
    def protegida(request, *args, **kwargs):
        if not eh_gestor(request.user):
            messages.error(request, 'Acesso restrito: esta página é só para gestores.')
            return redirect('lista_produtos')
        return view(request, *args, **kwargs)
    return protegida