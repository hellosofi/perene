// Equipe: o código de convite começa desfocado.
// O botão de olho mostra/esconde o código; o botão Copiar funciona nos dois estados.

const codigo = document.querySelector('[data-codigo-convite]');
const botaoOlho = document.querySelector('[data-mostrar-codigo]');
const botaoCopiar = document.querySelector('[data-copiar-codigo]');

if (codigo && botaoOlho) {
    botaoOlho.addEventListener('click', () => {
        const oculto = codigo.toggleAttribute('data-oculto');
        codigo.setAttribute('aria-hidden', oculto ? 'true' : 'false');
        botaoOlho.setAttribute('aria-pressed', oculto ? 'false' : 'true');
        botaoOlho.setAttribute('aria-label', oculto ? 'Mostrar código' : 'Esconder código');
        botaoOlho.querySelector('use').setAttribute('href', oculto ? '#icon-eye' : '#icon-eye-off');
    });
}

if (codigo && botaoCopiar) {
    const rotulo = botaoCopiar.querySelector('[data-copiar-rotulo]');

    botaoCopiar.addEventListener('click', async () => {
        try {
            await navigator.clipboard.writeText(codigo.textContent.trim());
            rotulo.textContent = 'Copiado!';
        } catch {
            rotulo.textContent = 'Não deu para copiar';
        }
        setTimeout(() => { rotulo.textContent = 'Copiar'; }, 2000);
    });
}
