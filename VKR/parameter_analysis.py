"""
Анализ параметров фильтра Бесселя:
1. Порядок фильтра (n = 1..5) — АЧХ и групповая задержка
2. Частота среза (fc = 2, 5, 10, 20 Гц)
3. Уровень шума (σ² = 0.01, 0.05, 0.1, 0.2, 0.5)
4. Размер усечения L (8, 16, 32, 64) — степени двойки
5. Сравнение трех базисов (тригонометрический, Лежандра, Хаара)
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.signal import bessel, freqs

from spectral_basis import SpectralBasis
from bessel_filter import BesselFilter
from test_signal import create_test_signal


def calculate_rmse(u, x):
    """Вычисляет RMSE между сигналами."""
    min_len = min(len(u), len(x))
    u = u[:min_len]
    x = x[:min_len]
    return np.sqrt(np.mean((u - x)**2))


def estimate_delay(t, u, x):
    """Оценивает фазовую задержку между входным и выходным сигналами."""
    min_len = min(len(u), len(x))
    u = u[:min_len]
    x = x[:min_len]
    t = t[:min_len]
    
    half = len(t) // 2
    u_steady = u[half:]
    x_steady = x[half:]
    
    u_centered = u_steady - np.mean(u_steady)
    x_centered = x_steady - np.mean(x_steady)
    
    correlation = np.correlate(u_centered, x_centered, mode='same')
    peak_idx = np.argmax(np.abs(correlation))
    center = len(correlation) // 2
    delay_samples = peak_idx - center
    
    dt = t[1] - t[0]
    delay = delay_samples * dt
    
    return abs(delay)


def compensate_delay(t, x, delay):
    """Компенсирует задержку в сигнале."""
    dt = t[1] - t[0]
    delay_samples = int(round(delay / dt))
    
    if delay_samples > 0 and delay_samples < len(x):
        x_comp = x[delay_samples:]
        t_comp = t[:-delay_samples]
    else:
        x_comp = x
        t_comp = t
    
    return t_comp, x_comp


def analyze_filter_order():
   #Влияние порядка фильтра Бесселя на АЧХ и групповую задержку
    print("\n" + "="*70)
    print("АНАЛИЗ 1: ВЛИЯНИЕ ПОРЯДКА ФИЛЬТРА")
    print("="*70)
    
    omega = np.logspace(-1, 1, 500)
    orders = [1, 2, 3, 4, 5]
    colors = plt.cm.viridis(np.linspace(0, 1, len(orders)))
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle('Влияние порядка фильтра Бесселя на частотные характеристики', fontsize=14)
    
    ax1 = axes[0]
    for n, color in zip(orders, colors):
        b, a = bessel(n, 1, analog=True, norm='phase')
        w, h = freqs(b, a, omega)
        ax1.semilogx(omega, 20*np.log10(np.abs(h)), color=color, linewidth=1.5, label=f'n = {n}')
    ax1.axhline(y=-3, color='gray', linestyle='--', alpha=0.7, label='-3 дБ')
    ax1.set_xlabel('Частота ω, рад/с')
    ax1.set_ylabel('Амплитуда, дБ')
    ax1.set_title('Амплитудно-частотная характеристика (ЛАЧХ)')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    ax1.set_xlim(0.1, 10)
    ax1.set_ylim(-40, 5)
    
    ax2 = axes[1]
    for n, color in zip(orders, colors):
        b, a = bessel(n, 1, analog=True, norm='phase')
        w, h = freqs(b, a, omega)
        phi = np.unwrap(np.angle(h))
        group_delay = -np.gradient(phi, omega)
        ax2.semilogx(omega, group_delay, color=color, linewidth=1.5, label=f'n = {n}')
    ax2.set_xlabel('Частота ω, рад/с')
    ax2.set_ylabel('Групповая задержка τ, с')
    ax2.set_title('Групповая задержка')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    ax2.set_xlim(0.1, 10)
    ax2.set_ylim(0, 3)
    
    plt.tight_layout()
    plt.show()
    
    


def analyze_cutoff_frequency():
    #Анализ 2: Влияние частоты среза на фильтрацию
    print("\n" + "="*70)
    print("АНАЛИЗ 2: ВЛИЯНИЕ ЧАСТОТЫ СРЕЗА")
    print("="*70)
    
    T = 2.0
    data = create_test_signal(T=T, fs=10000, seed=42)
    t, u_clean, g_noisy = data['t'], data['u'], data['g']
    g_func = interp1d(t, g_noisy, kind='cubic', bounds_error=False, fill_value=0)
    
    cutoff_freqs = [2.0, 5.0, 10.0, 20.0]
    L = 64  # Степень двойки
    order = 2
    basis_type = 'trigonometric'
    
    results = []
    plt.figure(figsize=(12, 10))
    
    for i, fc in enumerate(cutoff_freqs):
        basis = SpectralBasis(L, T, basis_type=basis_type)
        bessel_filter = BesselFilter(basis, order=order, cutoff_freq=fc)
        t_out, y = bessel_filter.apply_filter(g_func)
        
        u_interp = interp1d(t, u_clean, kind='cubic', bounds_error=False, fill_value=0)
        u_aligned = u_interp(t_out)
        
        # Оценка и компенсация задержки
        delay = estimate_delay(t_out, u_aligned, y)
        t_comp, y_comp = compensate_delay(t_out, y, delay)
        u_comp = u_interp(t_comp)
        
        rmse = calculate_rmse(u_comp, y_comp)
        results.append((fc, rmse))
        
        plt.subplot(2, 2, i + 1)
        n_show = 2000
        plt.plot(t_comp[:n_show], u_comp[:n_show], 'b-', linewidth=1, label='Исходный')
        plt.plot(t_comp[:n_show], y_comp[:n_show], 'r-', linewidth=1, label='Выход')
        plt.xlabel('Время (с)')
        plt.ylabel('Амплитуда')
        plt.title(f'f_c = {fc} Гц, RMSE = {rmse:.4f}')
        plt.legend(loc='upper right')
        plt.grid(True, alpha=0.3)
        plt.xlim([0, 0.3])
    
    plt.suptitle('Влияние частоты среза на качество фильтрации', fontsize=14)
    plt.tight_layout()
    plt.show()
    
    print("\nРезультаты:")
    for fc, rmse in results:
        print(f"  f_c = {fc:4.1f} Гц → RMSE = {rmse:.6f}")
    
    print("\nВыводы:")
    print("- При слишком низкой частоте среза (2 Гц) полезный сигнал подавляется")
    print("- При слишком высокой частоте среза (20 Гц) высокочастотные помехи проходят")
    print("- Оптимальная частота среза соответствует частоте полезного сигнала + запас")


def analyze_noise_level():
    #Анализ 3: Влияние уровня шума на качество фильтрации."""
    print("\n" + "="*70)
    print("АНАЛИЗ 3: ВЛИЯНИЕ УРОВНЯ ШУМА")
    print("="*70)
    
    T = 2.0
    fc = 5.0
    L = 64  # Степень двойки
    order = 2
    basis_type = 'trigonometric'
    
    noise_powers = [0.01, 0.05, 0.1, 0.2, 0.5]
    results = []
    
    for noise_power in noise_powers:
        np.random.seed(42)
        t = np.linspace(0, T, int(10000 * T))
        u = np.sin(2 * np.pi * 2.0 * t)
        v_noise = noise_power * np.random.randn(len(t))
        g = u + v_noise
        g_func = interp1d(t, g, kind='cubic', bounds_error=False, fill_value=0)
        
        basis = SpectralBasis(L, T, basis_type=basis_type)
        bessel_filter = BesselFilter(basis, order=order, cutoff_freq=fc)
        t_out, y = bessel_filter.apply_filter(g_func)
        
        u_interp = interp1d(t, u, kind='cubic', bounds_error=False, fill_value=0)
        u_aligned = u_interp(t_out)
        
        # Оценка и компенсация задержки
        delay = estimate_delay(t_out, u_aligned, y)
        t_comp, y_comp = compensate_delay(t_out, y, delay)
        u_comp = u_interp(t_comp)
        
        rmse = calculate_rmse(u_comp, y_comp)
        results.append((noise_power, rmse))
    
    plt.figure(figsize=(10, 6))
    noise_vals, rmse_vals = zip(*results)
    plt.plot(noise_vals, rmse_vals, 'b-o', linewidth=2, markersize=8)
    plt.xlabel('Мощность шума σ²')
    plt.ylabel('RMSE')
    plt.title('Влияние уровня шума на качество фильтрации')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    print("\nРезультаты:")
    for noise, rmse in results:
        print(f"  σ² = {noise:.2f} → RMSE = {rmse:.6f}")
    
    print("\nВыводы:")
    print("- С ростом уровня шума ошибка фильтрации увеличивается")
    print("- Зависимость близка к линейной в логарифмическом масштабе")


def analyze_convergence():
    #Анализ 4: Сходимость метода (влияние размера усечения L)
    print("\n" + "="*70)
    print("АНАЛИЗ 4: СХОДИМОСТЬ МЕТОДА (ВЛИЯНИЕ L)")
    print("="*70)
    
    # L как степени двойки (важно для базиса Хаара)
    L_values = [8, 16, 32, 64]
    T = 2.0
    fc = 5.0
    order = 2
    
    data = create_test_signal(T=T, fs=10000, seed=42)
    t, u_clean, g_noisy = data['t'], data['u'], data['g']
    g_func = interp1d(t, g_noisy, kind='cubic', bounds_error=False, fill_value=0)
    
    basis_types = ['trigonometric', 'legendre', 'haar']
    basis_names = {'trigonometric': 'косинусоид', 'legendre': 'Лежандра', 'haar': 'Хаара'}
    colors = {'trigonometric': 'blue', 'legendre': 'red', 'haar': 'green'}
    markers = {'trigonometric': 'o', 'legendre': 's', 'haar': '^'}
    
    plt.figure(figsize=(10, 6))
    
    print("\nРезультаты по базисам:")
    print("-" * 60)
    
    for basis_type in basis_types:
        errors = []
        for L in L_values:
            basis = SpectralBasis(L, T, basis_type=basis_type)
            bessel_filter = BesselFilter(basis, order=order, cutoff_freq=fc)
            t_out, y = bessel_filter.apply_filter(g_func)
            
            u_interp = interp1d(t, u_clean, kind='cubic', bounds_error=False, fill_value=0)
            u_aligned = u_interp(t_out)
            
            # Оценка и компенсация задержки
            delay = estimate_delay(t_out, u_aligned, y)
            t_comp, y_comp = compensate_delay(t_out, y, delay)
            u_comp = u_interp(t_comp)
            
            rmse = calculate_rmse(u_comp, y_comp)
            errors.append(rmse)
            print(f"  {basis_names[basis_type]:15} L={L:3d} → RMSE={rmse:.6f}")
        
        plt.semilogy(L_values, errors, color=colors[basis_type], marker=markers[basis_type],
                     linewidth=2, markersize=8, label=basis_names[basis_type])
    
    plt.xlabel('Размер усечения L (количество базисных функций)')
    plt.ylabel('RMSE')
    plt.title('Сходимость спектрального метода с ростом L')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()
    
    print("\nВыводы:")
    print("- С ростом L ошибка монотонно уменьшается для всех базисов")
    print("- Для достижения RMSE < 0.05 требуется L ≈ 64-128")
    print("- Базис Хаара сходится медленнее, требуя большего L")


def analyze_basis_comparison():
    #Анализ 5: Сравнение трех базисных систем."""
    print("\n" + "="*70)
    print("АНАЛИЗ 5: СРАВНЕНИЕ БАЗИСНЫХ СИСТЕМ")
    print("="*70)
    
    L = 64  # Степень двойки
    T = 2.0
    fc = 5.0
    order = 2
    
    data = create_test_signal(T=T, fs=10000, seed=42)
    t, u_clean, g_noisy = data['t'], data['u'], data['g']
    g_func = interp1d(t, g_noisy, kind='cubic', bounds_error=False, fill_value=0)
    
    basis_types = ['trigonometric', 'legendre', 'haar']
    basis_names = {'trigonometric': 'косинусоид', 'legendre': 'Лежандра', 'haar': 'Хаара'}
    colors = {'trigonometric': 'blue', 'legendre': 'red', 'haar': 'green'}
    
    results = []
    plt.figure(figsize=(12, 8))
    
    for i, basis_type in enumerate(basis_types):
        basis = SpectralBasis(L, T, basis_type=basis_type)
        bessel_filter = BesselFilter(basis, order=order, cutoff_freq=fc)
        t_out, y = bessel_filter.apply_filter(g_func)
        
        u_interp = interp1d(t, u_clean, kind='cubic', bounds_error=False, fill_value=0)
        u_aligned = u_interp(t_out)
        
        # Оценка и компенсация задержки
        delay = estimate_delay(t_out, u_aligned, y)
        t_comp, y_comp = compensate_delay(t_out, y, delay)
        u_comp = u_interp(t_comp)
        
        rmse = calculate_rmse(u_comp, y_comp)
        results.append((basis_names[basis_type], rmse))
        
        plt.subplot(2, 2, i + 1)
        n_show = 2000
        plt.plot(t_comp[:n_show], u_comp[:n_show], 'b-', linewidth=1, label='Исходный')
        plt.plot(t_comp[:n_show], y_comp[:n_show], color=colors[basis_type], 
                 linewidth=1.5, label=f'Выход ({basis_names[basis_type]})')
        plt.xlabel('Время (с)')
        plt.ylabel('Амплитуда')
        plt.title(f'Базис {basis_names[basis_type]}, RMSE = {rmse:.4f}')
        plt.legend(loc='upper right')
        plt.grid(True, alpha=0.3)
        plt.xlim([0, 0.3])
    
    plt.subplot(2, 2, 4)
    plt.axis('off')
    table_data = [[name, f"{rmse:.6f}"] for name, rmse in results]
    table = plt.table(cellText=table_data, colLabels=['Базис', 'RMSE'], 
                      loc='center', cellLoc='center', colWidths=[0.3, 0.3])
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    plt.title('Сводная таблица результатов', fontsize=12)
    
    plt.suptitle(f'Сравнение базисных систем (L={L}, f_c={fc} Гц)', fontsize=14)
    plt.tight_layout()
    plt.show()
    
    print("\nРезультаты:")
    for name, rmse in results:
        print(f"  {name:15} → RMSE = {rmse:.6f}")
    
    print("\nВыводы:")
    print("- Полиномы Лежандра дают наименьшую ошибку для гладких сигналов")
    print("- Тригонометрический базис также показывает хорошие результаты")
    print("- Базис Хаара наименее эффективен для гладкого сигнала,")
    print("  но может быть предпочтителен для сигналов с разрывами")


def run_all_analyses():
    """Запускает все анализы."""
    print("="*70)
    print("КОМПЛЕКСНЫЙ АНАЛИЗ ПАРАМЕТРОВ ФИЛЬТРА БЕССЕЛЯ")
    print("="*70)
    
    analyze_filter_order()
    analyze_cutoff_frequency()
    analyze_noise_level()
    analyze_convergence()
    analyze_basis_comparison()


if __name__ == "__main__":
    run_all_analyses()
