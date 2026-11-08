def mercado_do_usuario(user):
    """Devolve o mercado do usuário logado, ou None se ele não tiver perfil."""
    perfil = getattr(user, 'perfil', None)
    return perfil.mercado if perfil else None