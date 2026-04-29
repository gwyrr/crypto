/**
 * Este archivo maneja la autenticacion, la comunicacion con la API de FastAPI,
 * la actualizacion dinamica del DOM y la consulta de precios en tiempo real.
 */

const API_URL = ''; // Ruta relativa ya que el backend sirve los archivos estaticos

// --- ESTADO GLOBAL ---
let token = localStorage.getItem('crypto_token');

// --- ELEMENTOS DEL DOM ---
const authSection = document.getElementById('auth-section');
const dashboardSection = document.getElementById('dashboard-section');
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const txModal = document.getElementById('tx-modal');
const glassPanel = document.querySelector('.glass-panel');

// --- INICIALIZACION ---
// Si ya hay un token guardado, saltamos directamente al Dashboard
if (token) {
    showDashboard();
}

/**
 * Cambia visualmente entre las pestanas de Login y Registro.
 */
function switchAuthTab(tab) {
    const tabs = document.querySelectorAll('.tab');
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
 * Maneja el inicio de sesion enviando las credenciales al backend.
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
            body: params // OAuth2 utiliza form-urlencoded por defecto
        });

        const data = await res.json();

        if (!res.ok) throw new Error(data.detail || 'Error de inicio de sesion');

        // Guardamos el token para futuras peticiones autenticadas
        token = data.access_token;
        localStorage.setItem('crypto_token', token);
        showDashboard();
    } catch (err) {
        errorEl.textContent = err.message;
    }
}

/**
 * Maneja el registro de nuevos usuarios.
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

        // Si el registro es exitoso, hacemos login automatico
        switchAuthTab('login');
        document.getElementById('login-username').value = username;
        document.getElementById('login-password').value = password;
        handleLogin(new Event('submit'));
    } catch (err) {
        errorEl.textContent = err.message;
    }
}

/**
 * Cierra la sesion y limpia el almacenamiento local.
 */
function handleLogout() {
    token = null;
    localStorage.removeItem('crypto_token');
    dashboardSection.classList.add('hidden');
    authSection.classList.remove('hidden');
    authSection.classList.add('active');
    glassPanel.classList.remove('expanded');
}

/**
 * Muestra el panel principal y carga los datos del usuario.
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
 * Obtiene la lista de criptomonedas disponibles para operar.
 */
async function loadAssets() {
    try {
        const res = await fetch(`${API_URL}/assets/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const assets = await res.json();
        const select = document.getElementById('tx-asset-id');
        select.innerHTML = '<option value="">-- Seleccionar --</option>';
        assets.forEach(a => {
            const opt = document.createElement('option');
            opt.value = a.id;
            opt.textContent = `${a.symbol.toUpperCase()} - ${a.name}`;
            opt.dataset.apiId = a.api_id || a.symbol.toLowerCase();
            select.appendChild(opt);
        });
    } catch (err) {
        console.error('Error cargando activos:', err);
    }
}

/**
 * Consulta el precio actual del activo seleccionado mediante el backend (CoinGecko).
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
    if (!apiId) return;

    priceDisplay.style.display = 'block';
    priceDisplay.textContent = 'Obteniendo precio de mercado... ';

    try {
        const res = await fetch(`${API_URL}/market/prices?ids=${apiId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!res.ok) throw new Error('API Error');
        const data = await res.json();

        if (data[apiId] && data[apiId].usd) {
            const currentPrice = data[apiId].usd;
            priceDisplay.textContent = `Precio Actual: ${formatCurrency(currentPrice)}`;
            priceInput.value = currentPrice; // Autocompleta el precio para el usuario
        } else {
            priceDisplay.textContent = 'Precio no disponible.';
        }
    } catch (err) {
        priceDisplay.textContent = 'Error al obtener el precio actual.';
    }
}

/**
 * Carga el reporte del portafolio del usuario y actualiza la UI.
 */
async function loadPortfolio() {
    try {
        const res = await fetch(`${API_URL}/transactions/portfolio`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (res.status === 401) {
            handleLogout(); // Token expirado o invalido
            return;
        }

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Error al cargar el portafolio');

        // --- ACTUALIZAR TARJETAS DE RESUMEN ---
        document.getElementById('total-value').textContent = formatCurrency(data.current_total_value || 0);
        document.getElementById('total-invested').textContent = formatCurrency(data.total_investment || 0);

        const pnlEl = document.getElementById('total-pnl');
        pnlEl.textContent = formatCurrency(data.total_profit_loss || 0);
        pnlEl.className = (data.total_profit_loss || 0) >= 0 ? 'positive' : 'negative';

        // --- ACTUALIZAR TABLA DE ACTIVOS ---
        const tbody = document.getElementById('assets-tbody');
        tbody.innerHTML = '';

        if (data.assets) {
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
                `;
                tbody.appendChild(tr);
            });
        }

    } catch (err) {
        console.error("Error cargando portafolio:", err);
    }
}

// --- FUNCIONES DEL MODAL ---

function openTransactionModal() {
    txModal.classList.remove('hidden');
    document.getElementById('tx-error').textContent = '';
    document.getElementById('tx-form').reset();
    const priceDisplay = document.getElementById('current-price-display');
    if (priceDisplay) priceDisplay.style.display = 'none';
}

function closeTransactionModal() {
    txModal.classList.add('hidden');
}

/**
 * Envia una nueva transaccion al backend.
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
        loadPortfolio(); // Recargamos el dashboard para ver los cambios
    } catch (err) {
        errorEl.textContent = err.message;
    }
}

/**
 * Utilidad para dar formato de moneda USD a los numeros.
 */
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
}
