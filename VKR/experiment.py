"""
Модуль для проведения полного эксперимента по фильтрации с тремя базисами.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

from spectral_basis import SpectralBasis
from bessel_filter import BesselFilter
from test_signal import create_test_signal, analyze_spectrum


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


def calculate_error(u, x):
    """Вычисляет метрики ошибки между сигналами."""
    min_len = min(len(u), len(x))
    u = u[:min_len]
    x = x[:min_len]
    
    mse = np.mean((u - x)**2)
    rmse = np.sqrt(mse)
    max_error = np.max(np.abs(u - x))
    
    signal_amp = np.max(np.abs(u))
    if signal_amp > 0:
        relative_error = (rmse / signal_amp) * 100
    else:
        relative_error = 0
    
    correlation = np.corrcoef(u, x)[0, 1]
    
    return {
        'mse': mse, 'rmse': rmse, 'max_error': max_error,
        'relative_error': relative_error, 'correlation': correlation
    }


def print_error_report(error_metrics, title="РЕЗУЛЬТАТЫ ФИЛЬТРАЦИИ"):
    """Печатает отчет об ошибках."""
    print("\n" + "="*60)
    print(f"{title:^60}")
    print("="*60)
    print(f"Среднеквадратичная ошибка (MSE):      {error_metrics['mse']:.6f}")
    print(f"Корень из MSE (RMSE):                 {error_metrics['rmse']:.6f}")
    print(f"Максимальная абсолютная ошибка:       {error_metrics['max_error']:.6f}")
    print(f"Относительная ошибка:                 {error_metrics['relative_error']:.2f}%")
    print(f"Коэффициент корреляции:               {error_metrics['correlation']:.6f}")
    print("="*60)


def plot_filtering_result(t, u_clean, g_noisy, t_out, y, basis_type, filter_order, cutoff_freq):
 
    basis_names = {
        'trigonometric': 'косинусоиды',
        'legendre': 'полиномы Лежандра',
        'haar': 'функции Хаара'
    }
    basis_name_ru = basis_names.get(basis_type, basis_type)
    
    plt.figure(figsize=(14, 10))
    
    # График 1: Зашумленный сигнал (вход фильтра)
    plt.subplot(2, 1, 1)
    plt.plot(t, g_noisy, 'orange', linewidth=1.2, label='Зашумленный сигнал (вход фильтра)')
    plt.plot(t, u_clean, 'r-', linewidth=1.5, alpha=0.7, label='Полезный сигнал (для сравнения)')
    plt.xlabel('Время (с)')
    plt.ylabel('Амплитуда')
    plt.title(f'1. Зашумленный сигнал (вход фильтра) — виден шум и помехи')
    plt.legend(loc='upper right')
    plt.grid(True, alpha=0.3)
    plt.xlim([0, 2.0])
    
    # График 2: Очищенный сигнал (выход фильтра)
    plt.subplot(2, 1, 2)
    plt.plot(t_out, y, 'g-', linewidth=1.8, label='Оценка полезного сигнала (выход фильтра)')
    plt.plot(t, u_clean, 'r-', linewidth=1.5, alpha=0.7, label='Полезный сигнал (эталон)')
    plt.xlabel('Время (с)')
    plt.ylabel('Амплитуда')
    plt.title(f'2. Очищенный сигнал (выход фильтра) — шум подавлен, форма сохранена')
    plt.legend(loc='upper right')
    plt.grid(True, alpha=0.3)
    plt.xlim([0, 2.0])
    
    plt.suptitle(f'Фильтр Бесселя {filter_order}-го порядка, f_c = {cutoff_freq} Гц, базис: {basis_name_ru}', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()


def run_experiment(L=64, T=2.0, fc=5.0, order=2):
    
    print("="*70)
    print("ПОЛНЫЙ ЭКСПЕРИМЕНТ ПО ФИЛЬТРАЦИИ")
    print("="*70)
    print(f"\nПараметры эксперимента:")
    print(f"  Фильтр Бесселя: порядок = {order}, частота среза = {fc} Гц")
    print(f"  Размер усечения: L = {L} (степень двойки)")
    print(f"  Длительность сигнала: T = {T} с")
    print("="*70)
    
    basis_types = ['trigonometric', 'legendre', 'haar']
    
    basis_names = {
        'trigonometric': 'косинусоиды',
        'legendre': 'полиномы Лежандра',
        'haar': 'функции Хаара'
    }
    
    # Создаем тестовый сигнал
    data = create_test_signal(T=T, fs=10000, seed=42)
    t, u_clean, g_noisy = data['t'], data['u'], data['g']
    g_func = interp1d(t, g_noisy, kind='cubic', bounds_error=False, fill_value=0)
    
    results = {}
    
    for basis_type in basis_types:
        print(f"\n{'='*70}")
        print(f"ЭКСПЕРИМЕНТ: БАЗИС {basis_names[basis_type].upper()}")
        print(f"{'='*70}")
        
        basis = SpectralBasis(L, T, basis_type=basis_type)
        bessel_filter = BesselFilter(basis, order=order, cutoff_freq=fc)
        
        t_out, y = bessel_filter.apply_filter(g_func)
        
        # Два графика: зашумленный и очищенный
        plot_filtering_result(t, u_clean, g_noisy, t_out, y, basis_type, order, fc)
        
        # Оценка задержки и ошибки (для консоли)
        u_interp = interp1d(t, u_clean, kind='cubic', bounds_error=False, fill_value=0)
        u_aligned = u_interp(t_out)
        delay = estimate_delay(t_out, u_aligned, y)
        print(f"\nЗадержка: {delay*1000:.2f} мс")
        
        t_comp, y_comp = compensate_delay(t_out, y, delay)
        u_comp = u_interp(t_comp)
        
        error = calculate_error(u_comp, y_comp)
        print_error_report(error, f"БАЗИС {basis_names[basis_type].upper()}")
        
        results[basis_type] = error
    
    # Сводная таблица
    print("\n" + "="*70)
    print("СВОДНАЯ ТАБЛИЦА РЕЗУЛЬТАТОВ")
    print("="*70)
    print(f"{'Базис':<20} {'RMSE':<12} {'Корреляция':<12} {'Отн. ошибка (%)':<15}")
    print("-" * 65)
    for basis_type in basis_types:
        err = results[basis_type]
        basis_name_ru = basis_names[basis_type]
        print(f"{basis_name_ru:<20} {err['rmse']:<12.6f} {err['correlation']:<12.6f} {err['relative_error']:<15.2f}")
    
    return results


if __name__ == "__main__":
    # Запуск с L = 64 (степень двойки)
    run_experiment(L=64)
