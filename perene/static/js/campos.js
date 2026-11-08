// Telas de entrada: mostrar/esconder a senha e marcar o campo como válido.

document.querySelectorAll('[data-mostrar-senha]').forEach((botao) => {
    botao.addEventListener('click', () => {
        const campo = botao.parentElement.querySelector('input');
        const mostrar = campo.type === 'password';
        campo.type = mostrar ? 'text' : 'password';
        botao.setAttribute('aria-pressed', mostrar);
        botao.setAttribute('aria-label', mostrar ? 'Esconder senha' : 'Mostrar senha');
    });
});

// "Válido" só depois de sair do campo, com um valor aceito pelo navegador.
document.querySelectorAll('.campo input').forEach((campo) => {
    const caixa = campo.closest('.campo');
    campo.addEventListener('blur', () => {
        const valido = campo.value.trim() !== '' && campo.checkValidity();
        caixa.classList.toggle('campo--valido', valido);
        if (valido) {
            caixa.classList.remove('campo--erro');
        }
    });
    campo.addEventListener('input', () => caixa.classList.remove('campo--valido'));
});
