// Fecha o painel de notificações ao clicar fora dele.
document.addEventListener('click', (evento) => {
    const painel = document.querySelector('.notificacoes');
    if (painel && painel.open && !painel.contains(evento.target)) {
        painel.open = false;
    }
});
