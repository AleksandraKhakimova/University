"""
Интерактивное приложение для демонстрации фильтра Бесселя.
Использует готовые модули: spectral_basis, bessel_filter, test_signal.
Запуск: streamlit run app.py
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.signal import bessel, butter, freqs

# Импортируем ВАШИ готовые модули
from spectral_basis import SpectralBasis
from bessel_filter import BesselFilter
from test_signal import create_test_signal


# ============================================================================
# НАСТРОЙКА СТРАНИЦЫ
# ============================================================================

st.set_page_config(
    page_title="Фильтр Бесселя — интерактивная демонстрация",
    page_icon="🎛️",
    layout="wide"
)

st.title("🎛️ Фильтр Бесселя: интерактивная демонстрация")
st.markdown("""
    <div style='background-color: #f0f2f6; padding: 1rem; border-radius: 10px; margin-bottom: 1rem'>
    <b>Программная реализация линейных фильтров на основе ортогональных полиномов</b><br>
    <i>На примере фильтров Бесселя</i><br><br>
    🔹 <b>Подвиньте ползунки</b> — графики обновятся автоматически<br>
    🔹 <b>Сравните базисы</b> — выберите косинусоиды, полиномы Лежандра или функции Хаара
    </div>
""", unsafe_allow_html=True)


# ============================================================================
# БОКОВАЯ ПАНЕЛЬ С НАСТРОЙКАМИ
# ============================================================================

st.sidebar.header("⚙️ Настройки фильтра")

order = st.sidebar.slider(
    "Порядок фильтра n",
    min_value=1, max_value=8, value=2, step=1,
    help="Чем выше порядок, тем круче спад АЧХ"
)

cutoff_freq = st.sidebar.slider(
    "Частота среза f_c (Гц)",
    min_value=1.0, max_value=30.0, value=5.0, step=0.5,
    help="Частота, на которой сигнал ослабляется на 3 дБ"
)

st.sidebar.header("🎵 Настройки сигнала")

signal_freq = st.sidebar.slider(
    "Частота полезного сигнала (Гц)",
    min_value=0.5, max_value=10.0, value=2.0, step=0.5
)

noise_power = st.sidebar.slider(
    "Мощность шума σ²",
    min_value=0.0, max_value=0.5, value=0.1, step=0.01,
    help="Уровень белого шума"
)

st.sidebar.subheader("Высокочастотные помехи")

noise1_freq = st.sidebar.slider(
    "Помеха 1 (Гц)", min_value=10, max_value=300, value=45, step=5
)
noise1_amp = st.sidebar.slider(
    "Амплитуда помехи 1", min_value=0.0, max_value=0.5, value=0.2, step=0.05
)

noise2_freq = st.sidebar.slider(
    "Помеха 2 (Гц)", min_value=10, max_value=300, value=120, step=5
)
noise2_amp = st.sidebar.slider(
    "Амплитуда помехи 2", min_value=0.0, max_value=0.5, value=0.15, step=0.05
)

st.sidebar.header("📐 Настройки базиса")

basis_type = st.sidebar.selectbox(
    "Тип базиса",
    options=['trigonometric', 'legendre', 'haar'],
    format_func=lambda x: {
        'trigonometric': 'Косинусоиды',
        'legendre': 'Полиномы Лежандра',
        'haar': 'Функции Хаара'
    }[x]
)

L = st.sidebar.select_slider(
    "Количество базисных функций L",
    options=[8, 16, 32, 64, 128],
    value=64,
    help="Степень двойки для корректной работы базиса Хаара"
)

st.sidebar.header("📊 Отображение")

time_range = st.sidebar.slider(
    "Временной диапазон (с)", 
    min_value=0.1, max_value=2.0, value=0.5, step=0.1
)

show_group_delay = st.sidebar.checkbox("Показать групповую задержку", value=True)


# ============================================================================
# ФУНКЦИИ ДЛЯ ГЕНЕРАЦИИ СИГНАЛОВ И ФИЛЬТРАЦИИ
# ============================================================================

@st.cache_data
def generate_signals(signal_freq, noise_power, noise1_freq, noise1_amp, noise2_freq, noise2_amp):
    """Генерирует сигналы с заданными параметрами."""
    T = 2.0
    fs = 10000
    t = np.linspace(0, T, int(fs * T))
    
    # Полезный сигнал
    u = np.sin(2 * np.pi * signal_freq * t)
    
    # Высокочастотные помехи
    v_sin = (noise1_amp * np.sin(2 * np.pi * noise1_freq * t) +
             noise2_amp * np.sin(2 * np.pi * noise2_freq * t))
    
    # Белый шум
    np.random.seed(42)
    v_noise = noise_power * np.random.randn(len(t))
    
    # Суммарный сигнал
    v = v_sin + v_noise
    g = u + v
    
    return t, u, g, v_sin, v_noise


def apply_filter(t, g, basis_type, L, order, cutoff_freq):
    """Применяет фильтр к сигналу."""
    try:
        T = 2.0
        g_func = interp1d(t, g, kind='cubic', bounds_error=False, fill_value=0)
        
        # Используем ВАШ класс SpectralBasis
        basis = SpectralBasis(L, T, basis_type=basis_type)
        
        # Используем ВАШ класс BesselFilter
        bessel_filter = BesselFilter(basis, order=order, cutoff_freq=cutoff_freq)
        
        t_out, y = bessel_filter.apply_filter(g_func)
        return t_out, y, None
    except Exception as e:
        return None, None, str(e)


def compute_rmse(t, u, t_out, y):
    """Вычисляет RMSE между очищенным и полезным сигналом."""
    u_interp = interp1d(t, u, kind='cubic', bounds_error=False, fill_value=0)
    u_aligned = u_interp(t_out)
    min_len = min(len(u_aligned), len(y))
    rmse = np.sqrt(np.mean((u_aligned[:min_len] - y[:min_len])**2))
    return rmse


def compute_frequency_response(order, cutoff_freq, frequencies):
    """Вычисляет АЧХ фильтра."""
    omega_c = 2 * np.pi * cutoff_freq
    omega = 2 * np.pi * frequencies
    b, a = bessel(order, omega_c, analog=True, norm='phase')
    w, h = freqs(b, a, omega)
    return np.abs(h)


def compute_group_delay(order):
    """Вычисляет групповую задержку для сравнения Бесселя и Баттерворта."""
    omega = np.logspace(-1, 1, 300)
    group_delays = {'bessel': {}, 'butter': {}}
    
    for n in [2, 3, 4]:
        # Бессель
        b, a = bessel(n, 1, analog=True, norm='phase')
        w, h = freqs(b, a, omega)
        phi = np.unwrap(np.angle(h))
        group_delays['bessel'][n] = -np.gradient(phi, omega)
        
        # Баттерворт
        b, a = butter(n, 1, analog=True)
        w, h = freqs(b, a, omega)
        phi = np.unwrap(np.angle(h))
        group_delays['butter'][n] = -np.gradient(phi, omega)
    
    return omega, group_delays


# ============================================================================
# ГЕНЕРАЦИЯ ДАННЫХ
# ============================================================================

# Генерируем сигналы
t, u, g, v_sin, v_noise = generate_signals(
    signal_freq, noise_power, noise1_freq, noise1_amp, noise2_freq, noise2_amp
)

# Применяем фильтр
t_out, y, error = apply_filter(t, g, basis_type, L, order, cutoff_freq)


# ============================================================================
# ОСНОВНАЯ ЧАСТЬ: ГРАФИКИ
# ============================================================================

if error:
    st.error(f"Ошибка при применении фильтра: {error}")
else:
    # Вычисляем RMSE
    rmse = compute_rmse(t, u, t_out, y)
    
    # Отображаем метрики
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📊 RMSE", f"{rmse:.6f}")
    col2.metric("🎛️ Порядок фильтра", order)
    col3.metric("📡 Частота среза", f"{cutoff_freq} Гц")
    col4.metric("📐 Базис", {
        'trigonometric': 'Косинусоиды',
        'legendre': 'Лежандра',
        'haar': 'Хаара'
    }[basis_type])
    
    # ========================================================================
    # ГРАФИК 1: ВХОДНОЙ И ВЫХОДНОЙ СИГНАЛЫ
    # ========================================================================
    
    st.subheader("📈 Результат фильтрации")
    
    # Создаем два графика
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # График 1: Зашумленный сигнал (вход)
    n_show = int(time_range * 10000)
    ax1.plot(t[:n_show], g[:n_show], 'orange', linewidth=1.2, label='Зашумленный сигнал (вход)')
    ax1.plot(t[:n_show], u[:n_show], 'r--', linewidth=1.5, alpha=0.7, label='Полезный сигнал')
    ax1.set_xlabel('Время (с)')
    ax1.set_ylabel('Амплитуда')
    ax1.set_title('Зашумленный сигнал (вход фильтра)')
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, time_range)
    
    # График 2: Очищенный сигнал (выход)
    u_interp = interp1d(t, u, kind='cubic', bounds_error=False, fill_value=0)
    mask = t_out <= time_range
    ax2.plot(t_out[mask], y[mask], 'green', linewidth=1.8, label='Очищенный сигнал (выход)')
    ax2.plot(t_out[mask], u_interp(t_out[mask]), 'r--', linewidth=1.5, alpha=0.7, label='Полезный сигнал')
    ax2.set_xlabel('Время (с)')
    ax2.set_ylabel('Амплитуда')
    ax2.set_title('Очищенный сигнал (выход фильтра)')
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0, time_range)
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # ========================================================================
    # ГРАФИК 2: АЧХ И СПЕКТРЫ
    # ========================================================================
    
    st.subheader("📊 Частотные характеристики")
    
    fig2, (ax_freq, ax_spec) = plt.subplots(1, 2, figsize=(12, 5))
    
    # АЧХ фильтра
    frequencies = np.logspace(0, 2.5, 200)
    H = compute_frequency_response(order, cutoff_freq, frequencies)
    ax_freq.semilogx(frequencies, H, 'b-', linewidth=2, label='АЧХ фильтра')
    ax_freq.axvline(x=cutoff_freq, color='r', linestyle='--', label=f'f_c = {cutoff_freq} Гц')
    ax_freq.set_xlabel('Частота (Гц)')
    ax_freq.set_ylabel('|H(f)|')
    ax_freq.set_title('Амплитудно-частотная характеристика')
    ax_freq.legend()
    ax_freq.grid(True, alpha=0.3)
    ax_freq.set_xlim(1, 300)
    ax_freq.set_ylim(0, 1.1)
    
    # Спектры сигналов
    dt = t[1] - t[0]
    n = len(g)
    fft_g = np.fft.fft(g)
    fft_u = np.fft.fft(u)
    freqs_fft = np.fft.fftfreq(n, dt)
    
    positive = freqs_fft > 0
    mask_freq = freqs_fft[positive] < 300
    
    spec_g = np.abs(fft_g[positive]) * 2.0 / n
    spec_u = np.abs(fft_u[positive]) * 2.0 / n
    
    ax_spec.semilogy(freqs_fft[positive][mask_freq], spec_g[mask_freq], 
                     'orange', linewidth=1.2, label='Зашумленный сигнал')
    ax_spec.semilogy(freqs_fft[positive][mask_freq], spec_u[mask_freq], 
                     'r--', linewidth=1.5, label='Полезный сигнал')
    ax_spec.axvline(x=cutoff_freq, color='g', linestyle='--', label=f'f_c = {cutoff_freq} Гц')
    ax_spec.axvline(x=signal_freq, color='r', linestyle=':', label=f'f_сигнала = {signal_freq} Гц')
    ax_spec.set_xlabel('Частота (Гц)')
    ax_spec.set_ylabel('Амплитуда')
    ax_spec.set_title('Спектры сигналов')
    ax_spec.legend(loc='upper right')
    ax_spec.grid(True, alpha=0.3)
    ax_spec.set_xlim(0, 300)
    
    plt.tight_layout()
    st.pyplot(fig2)
    
    # ========================================================================
    # ГРАФИК 3: ГРУППОВАЯ ЗАДЕРЖКА (опционально)
    # ========================================================================
    
    if show_group_delay:
        st.subheader("📉 Групповая задержка (сравнение Бесселя и Баттерворта)")
        st.markdown("""
            <div style='background-color: #e8f4f8; padding: 0.5rem; border-radius: 5px; margin-bottom: 1rem'>
            <b>Почему это важно?</b> У фильтра Бесселя групповая задержка максимально плоская 
            в полосе пропускания, что обеспечивает сохранение формы сигнала.
            </div>
        """, unsafe_allow_html=True)
        
        omega, group_delays = compute_group_delay(order)
        
        fig3, ax = plt.subplots(1, 1, figsize=(10, 5))
        
        colors = ['blue', 'red', 'green']
        for n, color in zip([2, 3, 4], colors):
            ax.semilogx(omega, group_delays['bessel'][n], color=color, 
                       linewidth=2, label=f'Бессель n={n}')
            ax.semilogx(omega, group_delays['butter'][n], color=color, 
                       linewidth=1.5, linestyle='--', label=f'Баттерворт n={n}')
        
        ax.set_xlabel('Частота ω, рад/с')
        ax.set_ylabel('Групповая задержка τ, с')
        ax.set_title('Сравнение групповой задержки фильтров Бесселя и Баттерворта')
        ax.legend(loc='upper right', ncol=2, fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0.1, 10)
        ax.set_ylim(0, 3)
        
        plt.tight_layout()
        st.pyplot(fig3)
    
    # ========================================================================
    # ВЫВОДЫ
    # ========================================================================
    
    st.markdown("---")
    st.subheader("📝 Анализ результатов")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **🔵 Фильтр Бесселя**
        - ✅ Максимально плоская групповая задержка
        - ✅ Сохраняет форму сигнала
        - ✅ Нет выбросов на переходных процессах
        - ❌ Более пологий спад АЧХ
        """)
    
    with col2:
        if rmse < 0.05:
            st.success(f"✅ **Отлично!** RMSE = {rmse:.6f}")
            st.write("Фильтр успешно подавил шум и сохранил форму сигнала.")
        elif rmse < 0.1:
            st.warning(f"⚠️ **Удовлетворительно** RMSE = {rmse:.6f}")
            st.write("Качество фильтрации приемлемое, но возможны улучшения.")
        else:
            st.error(f"❌ **Плохо** RMSE = {rmse:.6f}")
            st.write("Попробуйте изменить параметры фильтра или частоту среза.")
        
        st.write(f"""
        **Текущая конфигурация:**
        - Порядок: {order}
        - Частота среза: {cutoff_freq} Гц
        - Базис: {basis_type}
        - L = {L}
        """)
    
    # ========================================================================
    # ИНФОРМАЦИЯ О СИГНАЛЕ
    # ========================================================================
    
    with st.expander("📊 Детальная информация о сигнале"):
        col1, col2, col3 = st.columns(3)
        col1.write(f"**Полезный сигнал:** {signal_freq} Гц")
        col2.write(f"**Помеха 1:** {noise1_freq} Гц, амплитуда {noise1_amp}")
        col3.write(f"**Помеха 2:** {noise2_freq} Гц, амплитуда {noise2_amp}")
        
        # Вычисляем SNR
        signal_power = np.mean(u**2)
        noise_power_total = np.mean((g - u)**2)
        snr_db = 10 * np.log10(signal_power / noise_power_total)
        st.write(f"**Отношение сигнал/шум (SNR):** {snr_db:.2f} дБ")


# ============================================================================
# ИНФОРМАЦИЯ В БОКОВОЙ ПАНЕЛИ
# ============================================================================

st.sidebar.markdown("---")
st.sidebar.info("""
**💡 Советы по настройке:**

1. **Порядок фильтра:** 
   - n=2-3 — оптимальный компромисс
   - n>5 — избыточно

2. **Частота среза:**
   - Должна быть выше частоты сигнала
   - Слишком низкая — подавляет сигнал
   - Слишком высокая — пропускает шум

3. **Базис:**
   - Косинусоиды — универсальный
   - Лежандра — лучший для гладких сигналов
   - Хаара — для сигналов с разрывами

4. **L:** 64 достаточно для хорошей точности
""")

st.sidebar.markdown("---")
st.sidebar.caption("""
**Дипломная работа**  
Программная реализация линейных фильтров  
на основе ортогональных полиномов  
(на примере фильтров Бесселя)
""")
