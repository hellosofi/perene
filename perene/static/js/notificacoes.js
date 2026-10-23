document.addEventListener('click', (evento) => {
    const ancora = document.querySelector('.ancora-notificacao');
    if (ancora && ancora.open && !ancora.contains(evento.target)) {
        ancora.open = false;
    }
});