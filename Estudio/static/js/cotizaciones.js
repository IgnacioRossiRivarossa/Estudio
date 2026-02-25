'use strict';
/**
 * Devuelve los colores del dataset activo según el tema (light/dark).
 * @returns {{ textColor: string, gridColor: string, tooltipBg: string, tooltipText: string }}
 */
function getThemeColors() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    return {
        textColor:   isDark ? '#b8bcc4' : '#4a5568',
        gridColor:   isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.06)',
        tooltipBg:   isDark ? '#232833' : '#ffffff',
        tooltipText: isDark ? '#e8eaed' : '#233142',
    };
}
/**
 * @param {string} fecha
 * @returns {string}
 */
function formatLabelMes(fecha) {
    if (!fecha) return '';
    const partes = fecha.split('-');
    if (partes.length >= 2) {
        const meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                       'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
        const mes  = parseInt(partes[1], 10);
        const anio = partes[0].slice(2);
        return meses[mes - 1] + ' ' + anio;
    }
    return fecha;
}

/**
 * @param {string} fecha
 * @returns {string}
 */
function formatLabelDia(fecha) {
    if (!fecha) return '';
    const partes = fecha.split('-');
    if (partes.length === 3) {
        return partes[2] + '/' + partes[1];
    }
    return fecha;
}
/**
 * @param {{ textColor, gridColor, tooltipBg, tooltipText }} theme
 * @param {string} suffixY  
 * @param {boolean} useDayFormat 
 * @returns {object} 
 */
function buildChartOptions(theme, suffixY, useDayFormat) {
    return {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
            legend: { display: false },
            tooltip: {
                backgroundColor: theme.tooltipBg,
                titleColor:      theme.tooltipText,
                bodyColor:       theme.tooltipText,
                borderColor:     theme.gridColor,
                borderWidth:     1,
                padding:         12,
                cornerRadius:    8,
                callbacks: {
                    label: function (ctx) {
                        return ctx.parsed.y.toLocaleString('es-AR') + (suffixY || '');
                    },
                },
            },
        },
        scales: {
            x: {
                ticks: {
                    color:         theme.textColor,
                    font:          { size: 11 },
                    maxRotation:   45,
                    maxTicksLimit: 12,
                    callback: function (value) {
                        const label = this.getLabelForValue(value);
                        return useDayFormat ? formatLabelDia(label) : formatLabelMes(label);
                    },
                },
                grid: { display: false },
            },
            y: {
                ticks: {
                    color: theme.textColor,
                    font:  { size: 11 },
                    callback: function (value) {
                        return value.toLocaleString('es-AR') + (suffixY || '');
                    },
                },
                grid: { color: theme.gridColor },
            },
        },
    };
}
/**
 * @param {string}  canvasId     - ID del elemento <canvas>
 * @param {string[]} labels      - Etiquetas del eje X (fechas ISO)
 * @param {number[]} data        - Valores numéricos
 * @param {string}  color        - Color CSS rgb(...) sin alpha
 * @param {string}  suffixY      - Sufijo para tooltips y eje Y
 * @param {boolean} useDayFormat - Formato diario o mensual en eje X
 * @returns {Chart|null}
 */
function crearGrafico(canvasId, labels, data, color, suffixY, useDayFormat) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    const ctx    = canvas.getContext('2d');
    const theme  = getThemeColors();

    // Gradiente de relleno debajo de la línea
    const gradient = ctx.createLinearGradient(0, 0, 0, 280);
    gradient.addColorStop(0, color.replace(')', ', 0.25)').replace('rgb', 'rgba'));
    gradient.addColorStop(1, color.replace(')', ', 0.02)').replace('rgb', 'rgba'));

    return new Chart(canvas, {
        type: 'line',
        data: {
            labels:   labels,
            datasets: [{
                data:                    data,
                borderColor:             color,
                backgroundColor:         gradient,
                borderWidth:             2.5,
                pointRadius:             0,
                pointHoverRadius:        5,
                pointHoverBackgroundColor: color,
                pointHoverBorderColor:   '#fff',
                pointHoverBorderWidth:   2,
                tension:                 0.3,
                fill:                    true,
            }],
        },
        options: buildChartOptions(theme, suffixY, useDayFormat || false),
    });
}
/**
 * @param {number} segundos - Tiempo total de espera (por defecto 300)
 */
function iniciarAutoRefresh(segundos) {
    segundos = segundos || 300;
    const el = document.getElementById('countdown-seconds');

    setInterval(function () {
        segundos--;
        if (el) el.textContent = segundos;
        if (segundos <= 0) location.reload();
    }, 1000);
}

document.addEventListener('DOMContentLoaded', function () {
    // Los datos son inyectados por el template en window.COTIZACIONES_DATA
    var d = window.COTIZACIONES_DATA;
    if (!d) {
        console.warn('[cotizaciones] No se encontraron datos en window.COTIZACIONES_DATA');
        return;
    }

    crearGrafico('chart-inflacion',    d.inflLabels,    d.inflValores,   'rgb(255, 193, 7)',  '%', false);
    crearGrafico('chart-inflacion-ia', d.inflIaLabels,  d.inflIaValores, 'rgb(253, 126, 20)', '%', false);
    crearGrafico('chart-uva',          d.uvaLabels,     d.uvaValores,    'rgb(140, 79, 159)', '',  true);
    crearGrafico('chart-riesgo',       d.riesgoLabels,  d.riesgoValores, 'rgb(220, 53, 69)',  '',  true);

    iniciarAutoRefresh(300);
});
