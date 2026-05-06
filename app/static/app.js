/**
 * app.js - Logica principal del frontend de Crypto Portfolio Pro
 *
 * Modulos:
 *  1. Autenticacion (login, registro, logout)
 *  2. Portafolio (carga de activos y resumen financiero)
 *  3. Transacciones (modal con chart integrado)
 *  4. Charts (vista de velas candlestick con TradingView Lightweight Charts)
 */

const API_URL = '';

// --- ESTADO GLOBAL ---
let token = localStorage.getItem('crypto_token');
let currentChartDays = 7;        // Dias actuales del chart principal
let modalChartDays = 1;          // Dias del mini-chart en el modal
let mainChart = null;            // Instancia del chart principal
let mainCandleSeries = null;     // Serie de velas del chart principal
let modalChart = null;           // Instancia del mini-chart en modal
let modalCandleSeries = null;    // Serie de velas del modal

// --- ELEMENTOS DEL DOM ---
const authSection = document.getElementById('auth-section');
const dashboardSection = document.getElementById('dashboard-section');
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const txModal = document.getElementById('tx-modal');
const glassPanel = document.querySelector('.glass-panel');

// --- INICIALIZACION ---
if (token) {
    showDashboard();
}

// Calcular el total estimado de la transaccion en tiempo real
document.addEventListener('DOMContentLoaded', () => {
    const amountInput = document.getElementById('tx-amount');
    const priceInput = document.getElementById('tx-price');
    if (amountInput && priceInput) {
        [amountInput, priceInput].forEach(el => {
            el.addEventListener('input', updateTxTotalPreview);
        });
    }
});

// ===========================================================================
// SECCION 1: AUTENTICACION
// ===========================================================================

/**
 * Cambia entre las pestanas de Login y Registro.
 */
function switchAuthTab(tab) {
    const tabs = document.querySelectorAll('#auth-section .tab');
    tabs.forEach(t => t.classList.remove('active'));
    if (tab === 'login') {
        tabs[0].classList.add('active');
        loginForm.classList.add('active');
        registerForm.classList.remove('active');
    } else {
        tabs[1].classList.add('active');
        registerForm.classList.add('active');
        loginForm.classList.remove('active');
    }
}

/**
 * Envia las credenciales al backend y guarda el token JWT resultante.
 */
async function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    const errorEl = document.getElementById('login-error');
    errorEl.textContent = '';

    try {
        const params = new URLSearchParams();
        params.append('username', username);
        params.append('password', password);

        const res = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            body: params
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Error de inicio de sesion');

        token = data.access_token;
        localStorage.setItem('crypto_token', token);
        showDashboard();
    } catch (err) {
        errorEl.textContent = err.message;
    }
}

/**
 * Registra un nuevo usuario y hace login automatico.
 */
async function handleRegister(e) {
    e.preventDefault();
    const username = document.getElementById('reg-username').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    const errorEl = document.getElementById('reg-error');
    errorEl.textContent = '';

    try {
        const res = await fetch(`${API_URL}/users/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail?.[0]?.msg || data.detail || 'Error al registrar');

        switchAuthTab('login');
        document.getElementById('login-username').value = username;
        document.getElementById('login-password').value = password;
        handleLogin(new Event('submit'));
    } catch (err) {
        errorEl.textContent = err.message;
    }
}

/**
 * Cierra la sesion limpiando el token y el estado de los charts.
 */
function handleLogout() {
    token = null;
    localStorage.removeItem('crypto_token');
    // Destruir instancias de chart para evitar memory leaks
    if (mainChart) { mainChart.remove(); mainChart = null; }
    if (modalChart) { modalChart.remove(); modalChart = null; }
    dashboardSection.classList.add('hidden');
    authSection.classList.remove('hidden');
    authSection.classList.add('active');
    glassPanel.classList.remove('expanded');
}

// ===========================================================================
// SECCION 2: DASHBOARD Y PORTAFOLIO
// ===========================================================================

/**
 * Muestra el dashboard y carga los datos iniciales.
 */
function showDashboard() {
    authSection.classList.remove('active');
    authSection.classList.add('hidden');
    dashboardSection.classList.remove('hidden');
    glassPanel.classList.add('expanded');
    loadAssets();
    loadPortfolio();
}

/**
 * Cambia entre la vista de Portafolio y la vista de Graficas.
 */
function switchDashboardView(view) {
    // Actualizar tabs de navegacion
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    document.getElementById(`tab-${view}`).classList.add('active');

    // Mostrar/ocultar vistas
    document.getElementById('view-portfolio').classList.toggle('hidden', view !== 'portfolio');
    document.getElementById('view-charts').classList.toggle('hidden', view !== 'charts');

    // Inicializar el chart principal cuando se entra a esa vista
    if (view === 'charts') {
        // Pequeño delay para que el DOM termine de renderizar
        setTimeout(() => loadCandlestickChart(), 100);
    }
}

/**
 * Carga los activos disponibles en el selector del modal y en el portafolio.
 */
async function loadAssets() {
    try {
        const res = await fetch(`${API_URL}/assets/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const assets = await res.json();

        // Llenar el select del modal de transaccion
        const select = document.getElementById('tx-asset-id');
        select.innerHTML = '<option value="">-- Seleccionar --</option>';
        assets.forEach(a => {
            const opt = document.createElement('option');
            opt.value = a.id;
            opt.textContent = `${a.symbol.toUpperCase()} - ${a.name}`;
            opt.dataset.apiId = a.api_id || a.symbol.toLowerCase();
            opt.dataset.name = a.name;
            select.appendChild(opt);
        });

        // Tambien llenar el selector del chart principal con los activos del sistema
        const chartSelect = document.getElementById('chart-coin-select');
        if (assets.length > 0) {
            chartSelect.innerHTML = '';
            assets.forEach(a => {
                if (a.api_id) {
                    const opt = document.createElement('option');
                    opt.value = a.api_id;
                    opt.dataset.symbol = a.symbol.toUpperCase();
                    opt.textContent = `${a.name} (${a.symbol.toUpperCase()})`;
                    chartSelect.appendChild(opt);
                }
            });
        }
    } catch (err) {
        console.error('Error cargando activos:', err);
    }
}

/**
 * Carga el reporte del portafolio y actualiza la UI.
 */
async function loadPortfolio() {
    try {
        const res = await fetch(`${API_URL}/transactions/portfolio`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (res.status === 401) { handleLogout(); return; }

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Error al cargar el portafolio');

        // Actualizar tarjetas de resumen
        document.getElementById('total-value').textContent = formatCurrency(data.current_total_value || 0);
        document.getElementById('total-invested').textContent = formatCurrency(data.total_investment || 0);

        const pnlEl = document.getElementById('total-pnl');
        const pnl = data.total_profit_loss || 0;
        pnlEl.textContent = formatCurrency(pnl);
        pnlEl.className = pnl >= 0 ? 'positive' : 'negative';

        // Actualizar tabla de activos
        const tbody = document.getElementById('assets-tbody');
        tbody.innerHTML = '';

        if (data.assets && data.assets.length > 0) {
            data.assets.forEach(asset => {
                const tr = document.createElement('tr');
                const pnlClass = asset.profit_loss >= 0 ? 'positive' : 'negative';
                const price = asset.amount > 0 ? (asset.current_value / asset.amount) : 0;

                tr.innerHTML = `
                    <td><strong>${asset.symbol.toUpperCase()}</strong></td>
                    <td>${asset.amount.toFixed(6)}</td>
                    <td>${formatCurrency(price)}</td>
                    <td>${formatCurrency(asset.current_value)}</td>
                    <td class="${pnlClass}">${formatCurrency(asset.profit_loss)} (${asset.percentage_change.toFixed(2)}%)</td>
                    <td>
                        <button class="btn-chart-mini" onclick="quickViewChart('${asset.symbol.toLowerCase()}', '${asset.symbol.toUpperCase()}')">
                             Ver
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        } else {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align:center; color: var(--text-muted); padding: 40px;">
                        No tienes activos aun. Registra tu primera transaccion con el boton "+ Nueva Tx"
                    </td>
                </tr>
            `;
        }
    } catch (err) {
        console.error("Error cargando portafolio:", err);
    }
}

/**
 * Acceso rapido: abre la vista de Charts con una moneda especifica desde la tabla.
 */
function quickViewChart(apiId, symbol) {
    // Buscar la opcion correspondiente en el select del chart
    const chartSelect = document.getElementById('chart-coin-select');
    for (let i = 0; i < chartSelect.options.length; i++) {
        if (chartSelect.options[i].value === apiId ||
            chartSelect.options[i].dataset.symbol === symbol) {
            chartSelect.selectedIndex = i;
            break;
        }
    }
    switchDashboardView('charts');
}

// ===========================================================================
// SECCION 3: MODAL DE TRANSACCIONES
// ===========================================================================

/**
 * Abre el modal de nueva transaccion.
 */
function openTransactionModal() {
    txModal.classList.remove('hidden');
    document.getElementById('tx-error').textContent = '';
    document.getElementById('tx-form').reset();
    document.getElementById('current-price-display').style.display = 'none';
    document.getElementById('tx-total-preview').style.display = 'none';

    // Resetear el mini-chart
    const placeholder = document.getElementById('modal-chart-placeholder');
    const chartContainer = document.getElementById('modal-chart-container');
    placeholder.classList.remove('hidden');
    chartContainer.classList.add('hidden');
    if (modalChart) { modalChart.remove(); modalChart = null; }
}

/**
 * Cierra el modal y destruye el mini-chart.
 */
function closeTransactionModal() {
    txModal.classList.add('hidden');
    if (modalChart) { modalChart.remove(); modalChart = null; }
}

/**
 * Cuando el usuario elige un activo: obtiene precio actual y carga mini-chart.
 */
async function fetchAssetPrice() {
    const select = document.getElementById('tx-asset-id');
    const selectedOption = select.options[select.selectedIndex];
    const priceDisplay = document.getElementById('current-price-display');
    const priceInput = document.getElementById('tx-price');

    if (!selectedOption || !selectedOption.value) {
        priceDisplay.style.display = 'none';
        return;
    }

    const apiId = selectedOption.dataset.apiId;
    const name = selectedOption.dataset.name || apiId;
    if (!apiId) return;

    // Actualizar label del chart en el modal
    const symbol = selectedOption.textContent.split(' - ')[0];
    document.getElementById('modal-chart-label').textContent = `${symbol}/USD`;

    priceDisplay.style.display = 'block';
    priceDisplay.textContent = 'Cargando precio...';
    priceDisplay.className = '';

    // Cargar precio y mini-chart en paralelo
    const [priceResult] = await Promise.all([
        fetchPriceForAsset(apiId),
        loadModalChart(apiId, symbol)
    ]);

    if (priceResult !== null) {
        priceDisplay.textContent = `Precio actual: ${formatCurrency(priceResult)}`;
        priceDisplay.className = 'price-badge';
        priceInput.value = priceResult;
        updateTxTotalPreview();
    } else {
        priceDisplay.textContent = 'Precio no disponible';
    }
}

/**
 * Obtiene el precio actual de un activo. Retorna null si falla.
 */
async function fetchPriceForAsset(apiId) {
    try {
        const res = await fetch(`${API_URL}/market/prices?ids=${apiId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) return null;
        const data = await res.json();
        return (data[apiId] && data[apiId].usd) ? data[apiId].usd : null;
    } catch {
        return null;
    }
}

/**
 * Actualiza el preview del total estimado (cantidad * precio).
 */
function updateTxTotalPreview() {
    const amount = parseFloat(document.getElementById('tx-amount').value) || 0;
    const price = parseFloat(document.getElementById('tx-price').value) || 0;
    const previewEl = document.getElementById('tx-total-preview');
    const totalEl = document.getElementById('tx-total-value');

    if (amount > 0 && price > 0) {
        previewEl.style.display = 'flex';
        totalEl.textContent = formatCurrency(amount * price);
    } else {
        previewEl.style.display = 'none';
    }
}

/**
 * Envia la nueva transaccion al backend.
 */
async function submitTransaction(e) {
    e.preventDefault();
    const errorEl = document.getElementById('tx-error');
    errorEl.textContent = '';

    const type = document.getElementById('tx-type').value;
    const asset_id = parseInt(document.getElementById('tx-asset-id').value);
    const amount = parseFloat(document.getElementById('tx-amount').value);
    const buy_price = parseFloat(document.getElementById('tx-price').value);

    try {
        const res = await fetch(`${API_URL}/transactions/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ asset_id, amount, buy_price, type })
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Error en la transaccion');

        closeTransactionModal();
        loadPortfolio();
    } catch (err) {
        errorEl.textContent = err.message;
    }
}

// ===========================================================================
// SECCION 4: CHARTS CANDLESTICK (TradingView Lightweight Charts)
// ===========================================================================

/**
 * Crea o recrea el chart principal en la vista de Graficas.
 */
async function loadCandlestickChart() {
    const coinSelect = document.getElementById('chart-coin-select');
    if (!coinSelect || coinSelect.options.length === 0) return;

    const coinId = coinSelect.value;
    const symbol = coinSelect.options[coinSelect.selectedIndex]?.dataset?.symbol || coinId.toUpperCase();

    // Actualizar label de precio
    document.getElementById('chart-coin-label').textContent = `${symbol}/USD`;

    // Mostrar spinner
    showChartLoading(true);

    try {
        const candles = await fetchOhlcData(coinId, currentChartDays);

        // Destruir chart anterior si existe
        if (mainChart) {
            mainChart.remove();
            mainChart = null;
            mainCandleSeries = null;
        }

        // IMPORTANTE: mostrar el contenedor ANTES de crear el chart
        // para que clientWidth tenga un valor real y no sea 0
        showChartLoading(false);

        const container = document.getElementById('main-chart-container');
        container.innerHTML = '';

        // Pequeño delay para que el DOM actualice las dimensiones
        await new Promise(r => setTimeout(r, 30));

        const chartWidth = container.clientWidth || container.parentElement?.clientWidth || 800;

        // Crear chart con estilo oscuro estilo Binance
        mainChart = LightweightCharts.createChart(container, {
            ...buildChartOptions(container),
            width: chartWidth,
        });
        mainCandleSeries = mainChart.addCandlestickSeries(buildCandleSeriesOptions());

        mainCandleSeries.setData(candles);
        mainChart.timeScale().fitContent();

        // Actualizar info de la ultima vela
        if (candles.length > 0) {
            const last = candles[candles.length - 1];
            const first = candles[0];
            updateChartPriceInfo(last, first);
            updateCandleStats(last);
        }

        // Crosshair: actualizar stats al pasar sobre velas
        mainChart.subscribeCrosshairMove(param => {
            if (param.seriesData && param.seriesData.size > 0) {
                const data = param.seriesData.get(mainCandleSeries);
                if (data) updateCandleStats(data);
            }
        });

        // Chart responsivo
        const resizeObserver = new ResizeObserver(() => {
            if (mainChart && container.clientWidth > 0) {
                mainChart.applyOptions({ width: container.clientWidth });
            }
        });
        resizeObserver.observe(container);

    } catch (err) {
        console.error('Error cargando chart:', err);
        showChartError(`Error: ${err.message}`);
    }
}

/**
 * Carga el mini-chart dentro del modal de transacciones.
 */
async function loadModalChart(coinId, symbol) {
    const placeholder = document.getElementById('modal-chart-placeholder');
    const chartContainer = document.getElementById('modal-chart-container');

    // Destruir chart anterior
    if (modalChart) { modalChart.remove(); modalChart = null; }
    chartContainer.innerHTML = '';
    chartContainer.classList.add('hidden');
    placeholder.classList.remove('hidden');
    placeholder.innerHTML = '<div class="spinner small"></div><p>Cargando grafica...</p>';

    try {
        const candles = await fetchOhlcData(coinId, modalChartDays);

        // IMPORTANTE: mostrar el contenedor ANTES de crear el chart
        placeholder.classList.add('hidden');
        chartContainer.classList.remove('hidden');

        // Delay para que el DOM actualice las dimensiones
        await new Promise(r => setTimeout(r, 30));

        const chartWidth = chartContainer.clientWidth || chartContainer.parentElement?.clientWidth || 400;

        // Chart compacto para el modal
        modalChart = LightweightCharts.createChart(chartContainer, {
            ...buildChartOptions(chartContainer),
            width: chartWidth,
            height: 220,
        });
        modalCandleSeries = modalChart.addCandlestickSeries(buildCandleSeriesOptions());
        modalCandleSeries.setData(candles);
        modalChart.timeScale().fitContent();

        // Responsivo
        const resizeObserver = new ResizeObserver(() => {
            if (modalChart && chartContainer.clientWidth > 0) {
                modalChart.applyOptions({ width: chartContainer.clientWidth });
            }
        });
        resizeObserver.observe(chartContainer);

    } catch (err) {
        console.error('Error mini-chart:', err);
        placeholder.classList.remove('hidden');
        placeholder.innerHTML = `<p style="color:var(--danger)">Error: ${err.message}</p>`;
        chartContainer.classList.add('hidden');
    }
}

/**
 * Cambia el timeframe del chart principal y lo recarga.
 */
function setChartTimeframe(e, days) {
    currentChartDays = days;
    // Actualizar botones activos
    document.querySelectorAll('#view-charts .tf-btn').forEach(btn => btn.classList.remove('active'));
    if (e && e.target) e.target.classList.add('active');
    loadCandlestickChart();
}

/**
 * Cambia el timeframe del mini-chart en el modal.
 */
function setModalTimeframe(e, days) {
    modalChartDays = days;
    document.querySelectorAll('#tx-modal .tf-btn').forEach(btn => btn.classList.remove('active'));
    if (e && e.target) e.target.classList.add('active');

    const select = document.getElementById('tx-asset-id');
    const selectedOption = select.options[select.selectedIndex];
    if (selectedOption && selectedOption.dataset.apiId) {
        const symbol = selectedOption.textContent.split(' - ')[0];
        loadModalChart(selectedOption.dataset.apiId, symbol);
    }
}

/**
 * Consulta el endpoint OHLC del backend y retorna los datos de velas.
 */
async function fetchOhlcData(coinId, days) {
    const res = await fetch(`${API_URL}/market/ohlc/${coinId}?days=${days}`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Error ${res.status}`);
    }
    return await res.json();
}

/**
 * Construye las opciones base del chart con el tema oscuro estilo exchange.
 */
function buildChartOptions(container) {
    return {
        width: container.clientWidth || 800,
        height: 420,
        layout: {
            background: { type: 'solid', color: 'transparent' },
            textColor: '#94a3b8',
            fontSize: 12,
            fontFamily: 'Inter, sans-serif',
        },
        grid: {
            vertLines: { color: 'rgba(255,255,255,0.04)' },
            horzLines: { color: 'rgba(255,255,255,0.04)' },
        },
        crosshair: {
            mode: LightweightCharts.CrosshairMode.Normal,
            vertLine: {
                color: 'rgba(59,130,246,0.5)',
                labelBackgroundColor: '#3b82f6',
            },
            horzLine: {
                color: 'rgba(59,130,246,0.5)',
                labelBackgroundColor: '#3b82f6',
            },
        },
        rightPriceScale: {
            borderColor: 'rgba(255,255,255,0.08)',
            textColor: '#94a3b8',
        },
        timeScale: {
            borderColor: 'rgba(255,255,255,0.08)',
            timeVisible: true,
            secondsVisible: false,
            rightOffset: 5,
        },
    };
}

/**
 * Opciones de color para las velas (verde subida / rojo bajada).
 */
function buildCandleSeriesOptions() {
    return {
        upColor: '#10b981',
        downColor: '#ef4444',
        borderVisible: false,
        wickUpColor: '#10b981',
        wickDownColor: '#ef4444',
    };
}

/**
 * Actualiza el panel de precio actual del chart principal.
 */
function updateChartPriceInfo(lastCandle, firstCandle) {
    const priceEl = document.getElementById('chart-current-price');
    const changeEl = document.getElementById('chart-price-change');

    priceEl.textContent = formatCurrency(lastCandle.close);

    const change = lastCandle.close - firstCandle.open;
    const changePct = (change / firstCandle.open) * 100;
    const sign = change >= 0 ? '+' : '';
    changeEl.textContent = `${sign}${formatCurrency(change)} (${sign}${changePct.toFixed(2)}%)`;
    changeEl.className = `chart-price-change ${change >= 0 ? 'positive' : 'negative'}`;
}

/**
 * Actualiza el panel de stats (OHLC) de la vela bajo el cursor.
 */
function updateCandleStats(candle) {
    document.getElementById('stat-open').textContent = formatCurrency(candle.open);
    document.getElementById('stat-high').textContent = formatCurrency(candle.high);
    document.getElementById('stat-low').textContent = formatCurrency(candle.low);
    document.getElementById('stat-close').textContent = formatCurrency(candle.close);
}

/**
 * Muestra u oculta el spinner de carga del chart principal.
 */
function showChartLoading(visible) {
    document.getElementById('chart-loading').style.display = visible ? 'flex' : 'none';
    document.getElementById('main-chart-container').style.display = visible ? 'none' : 'block';
}

/**
 * Muestra un mensaje de error en el area del chart.
 */
function showChartError(msg) {
    const loadingEl = document.getElementById('chart-loading');
    loadingEl.style.display = 'flex';
    loadingEl.innerHTML = `<p style="color:var(--danger); text-align:center; padding:20px;">${msg}</p>`;
    document.getElementById('main-chart-container').style.display = 'none';
}

// ===========================================================================
// UTILIDADES
// ===========================================================================

/**
 * Formatea un numero como moneda USD.
 */
function formatCurrency(value) {
    if (value === null || value === undefined) return '--';
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
}
