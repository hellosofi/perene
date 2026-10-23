function alternarVisao(visao) {
    document.getElementById('campo-visao').value = visao;
    document.getElementById('form-filtros').submit();
}

function alternarStatus(status) {
    const campo = document.getElementById('campo-status');
    // clicar de novo no filtro ativo desmarca
    campo.value = campo.value === status ? '' : status;
    document.getElementById('form-filtros').submit();
}
