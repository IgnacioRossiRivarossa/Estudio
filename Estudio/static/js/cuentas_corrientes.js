function formatoAR(value) {
    const num = parseFloat(value) || 0;
    return num.toLocaleString('es-AR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    });
}

function parsearAR(str) {
    if (str === null || str === undefined || str === '') return 0;
    str = String(str).trim();
    if (str.includes(',')) {
        str = str.replace(/\./g, '').replace(',', '.');
    }
    return parseFloat(str) || 0;
}

function getCSRFToken() {
    if (typeof csrfToken !== 'undefined' && csrfToken) {
        return csrfToken;
    }
    // Fallback: leer de cookie
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith('csrftoken=')) {
            return cookie.substring('csrftoken='.length);
        }
    }
    return '';
}

function habilitarEdicion(btn) {
    const row = btn.closest('tr');
    row.dataset.originalValues = JSON.stringify(getRowValues(row));
    const editableCells = row.querySelectorAll('td[data-field="vencido"], td[data-field="balance_especial"], td[data-field="mes"]');
    editableCells.forEach(cell => {
        const rawValue = cell.dataset.value || '0';
        const numValue = parseFloat(rawValue) || 0;
        const formatted = formatoAR(numValue);
        cell.innerHTML = `<input type="text" inputmode="decimal" class="cell-input" value="${formatted}">`;
    });
    row.querySelector('.btn-edit-row').classList.add('d-none');
    row.querySelector('.btn-save-row').classList.remove('d-none');
    row.querySelector('.btn-cancel-row').classList.remove('d-none');
}

function getRowValues(row) {
    const values = {};
    const vencidoCell = row.querySelector('td[data-field="vencido"]');
    const balanceCell = row.querySelector('td[data-field="balance_especial"]');

    values.vencido = vencidoCell.dataset.value || '0';
    values.balance_especial = balanceCell.dataset.value || '0';
    values.meses = {};

    row.querySelectorAll('td[data-field="mes"]').forEach(cell => {
        const periodo = cell.dataset.periodo;
        values.meses[periodo] = cell.dataset.value || '0';
    });

    return values;
}

function cancelarEdicion(btn) {
    const row = btn.closest('tr');
    const original = JSON.parse(row.dataset.originalValues);
    const vencidoCell = row.querySelector('td[data-field="vencido"]');
    vencidoCell.dataset.value = original.vencido;
    vencidoCell.textContent = formatoAR(original.vencido);
    const balanceCell = row.querySelector('td[data-field="balance_especial"]');
    balanceCell.dataset.value = original.balance_especial;
    balanceCell.textContent = formatoAR(original.balance_especial);
    row.querySelectorAll('td[data-field="mes"]').forEach(cell => {
        const periodo = cell.dataset.periodo;
        const val = original.meses[periodo] || '0';
        cell.dataset.value = val;
        cell.textContent = formatoAR(val);
    });
    row.querySelector('.btn-edit-row').classList.remove('d-none');
    row.querySelector('.btn-save-row').classList.add('d-none');
    row.querySelector('.btn-cancel-row').classList.add('d-none');
}

async function guardarFila(btn) {
    const row = btn.closest('tr');
    const clienteId = row.dataset.clienteId;
    const vencidoInput = row.querySelector('td[data-field="vencido"] input');
    const balanceInput = row.querySelector('td[data-field="balance_especial"] input');

    const vencido = parsearAR(vencidoInput ? vencidoInput.value : '0');
    const balance_especial = parsearAR(balanceInput ? balanceInput.value : '0');

    const meses = {};
    row.querySelectorAll('td[data-field="mes"]').forEach(cell => {
        const periodo = cell.dataset.periodo;
        const input = cell.querySelector('input');
        if (input) {
            meses[periodo] = parsearAR(input.value);
        }
    });

    const payload = {
        cliente_id: clienteId,
        vencido: vencido,
        balance_especial: balance_especial,
        meses: meses,
    };

    btn.disabled = true;
    const cancelBtn = row.querySelector('.btn-cancel-row');
    cancelBtn.disabled = true;

    try {
        const response = await fetch(editarFilaUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            body: JSON.stringify(payload),
        });

        const data = await response.json();

        if (data.ok) {
            const vencidoCell = row.querySelector('td[data-field="vencido"]');
            vencidoCell.dataset.value = data.vencido;
            vencidoCell.textContent = formatoAR(data.vencido);
            const balanceCell = row.querySelector('td[data-field="balance_especial"]');
            balanceCell.dataset.value = data.balance_especial;
            balanceCell.textContent = formatoAR(data.balance_especial);
            row.querySelectorAll('td[data-field="mes"]').forEach(cell => {
                const periodo = cell.dataset.periodo;
                const val = data.meses[periodo] || '0';
                cell.dataset.value = val;
                cell.textContent = formatoAR(val);
            });
            const saldoCell = row.querySelector('td[data-field="saldo"]');
            saldoCell.textContent = formatoAR(data.saldo);
            row.querySelector('.btn-edit-row').classList.remove('d-none');
            row.querySelector('.btn-save-row').classList.add('d-none');
            row.querySelector('.btn-cancel-row').classList.add('d-none');
            recalcularTotales();
        } else {
            alert('Error al guardar: ' + (data.error || 'Error desconocido'));
        }
    } catch (error) {
        alert('Error de conexión al guardar los cambios.');
        console.error('Error:', error);
    } finally {
        btn.disabled = false;
        cancelBtn.disabled = false;
    }
}

function recalcularTotales() {
    const tabla = document.getElementById('tabla-cc');
    if (!tabla) return;
    const tbody = tabla.querySelector('tbody');
    const tfoot = tabla.querySelector('tfoot');
    if (!tfoot) return;

    const filas = tbody.querySelectorAll('tr[data-cliente-id]');
    if (filas.length === 0) return;

    let totalSaldo = 0;
    let totalVencido = 0;
    let totalBalance = 0;

    const primeraMeses = filas[0].querySelectorAll('td[data-field="mes"]');
    const totalMeses = new Array(primeraMeses.length).fill(0);

    filas.forEach(row => {
        const vCell = row.querySelector('td[data-field="vencido"]');
        const bCell = row.querySelector('td[data-field="balance_especial"]');
        const sCell = row.querySelector('td[data-field="saldo"]');

        totalVencido += parseFloat(vCell.dataset.value) || parsearAR(vCell.textContent);
        totalBalance += parseFloat(bCell.dataset.value) || parsearAR(bCell.textContent);
        totalSaldo += parsearAR(sCell.textContent);

        row.querySelectorAll('td[data-field="mes"]').forEach((mCell, idx) => {
            totalMeses[idx] += parseFloat(mCell.dataset.value) || parsearAR(mCell.textContent);
        });
    });

    const saldoTotal = tfoot.querySelector('td[data-total="saldo"]');
    if (saldoTotal) saldoTotal.innerHTML = '<strong>' + formatoAR(totalSaldo) + '</strong>';

    const vencidoTotal = tfoot.querySelector('td[data-total="vencido"]');
    if (vencidoTotal) vencidoTotal.innerHTML = '<strong>' + formatoAR(totalVencido) + '</strong>';

    const balanceTotal = tfoot.querySelector('td[data-total="balance_especial"]');
    if (balanceTotal) balanceTotal.innerHTML = '<strong>' + formatoAR(totalBalance) + '</strong>';

    totalMeses.forEach((total, idx) => {
        const mTotal = tfoot.querySelector(`td[data-total="mes-${idx}"]`);
        if (mTotal) mTotal.innerHTML = '<strong>' + formatoAR(total) + '</strong>';
    });
}
