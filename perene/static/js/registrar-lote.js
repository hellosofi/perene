// Registrar lote: atualiza a prévia "Como este lote vai aparecer" enquanto a pessoa preenche.
// A regra é a mesma do Lote.situacao no models.py (sem o estoque mínimo, que depende dos outros lotes).

const previa = document.querySelector('.previa-lote');

if (previa) {
    const diasAlerta = Number(previa.dataset.diasAlerta);
    const unidade = previa.dataset.unidade;
    const campoQuantidade = document.querySelector('[name=quantidade]');
    const campoValidade = document.querySelector('[name=validade]');
    const campoAvariado = document.querySelector('[name=avariado]');
    const detalhe = previa.querySelector('[data-previa-detalhe]');
    const etiqueta = previa.querySelector('[data-previa-situacao]');

    const atualizar = () => {
        const partes = [];
        if (campoQuantidade.value) {
            partes.push(`${campoQuantidade.value} ${unidade}`);
        }

        let situacao = 'ok';
        let texto = 'sem validade';

        if (campoValidade.value) {
            const hoje = new Date();
            hoje.setHours(0, 0, 0, 0);
            const validade = new Date(`${campoValidade.value}T00:00`);
            const dias = Math.round((validade - hoje) / 86400000);
            partes.push(`vence ${validade.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })}`);

            if (dias < 0) {
                situacao = 'critico';
                texto = `venceu há ${-dias} dia(s)`;
            } else if (dias <= diasAlerta) {
                situacao = 'atencao';
                texto = dias === 0 ? 'vence hoje' : `vence em ${dias} dia(s)`;
            } else {
                texto = `vence em ${dias} dia(s)`;
            }
        }

        if (campoAvariado.checked) {
            situacao = 'critico';
            texto = 'avariado';
        }

        const rotulos = { ok: 'Tudo certo', atencao: 'Atenção', critico: 'Crítico' };
        detalhe.textContent = partes.length ? partes.join(' · ') : 'Preencha a quantidade e a validade.';
        etiqueta.className = `etiqueta etiqueta--${situacao}`;
        etiqueta.textContent = `${rotulos[situacao]} · ${texto}`;
    };

    [campoQuantidade, campoValidade, campoAvariado].forEach((campo) => {
        campo.addEventListener('input', atualizar);
        campo.addEventListener('change', atualizar);
    });
    atualizar();
}
