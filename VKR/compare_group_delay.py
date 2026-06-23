"""
Сравнение групповой задержки фильтров Бесселя, Баттерворта и Чебышева I типа.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import bessel, butter, cheby1, freqs


def compare_group_delay():
    """Сравнивает групповую задержку фильтров Бесселя, Баттерворта и Чебышева."""
    
    print("="*70)
    print("СРАВНЕНИЕ ГРУППОВОЙ ЗАДЕРЖКИ: БЕССЕЛЬ, БАТТЕРВОРТ И ЧЕБЫШЕВ")
    print("="*70)
    
    omega = np.logspace(-1, 1, 500)  # Частоты от 0.1 до 10 рад/с
    orders = [2, 3, 4]
    colors = ['blue', 'red', 'green']
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    # Групповая задержка Бесселя
    ax1 = axes[0]
    for n, color in zip(orders, colors):
        b, a = bessel(n, 1, analog=True, norm='phase')
        w, h = freqs(b, a, omega)
        
        phi = np.unwrap(np.angle(h))
        group_delay = -np.gradient(phi, omega)
        
        ax1.semilogx(omega, group_delay, color=color, linewidth=2,
                     label=f'Бесселя, n = {n}')
    
    ax1.set_xlabel('Частота ω, рад/с')
    ax1.set_ylabel('Групповая задержка τ, с')
    ax1.set_title('Фильтры Бесселя')
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.legend(loc='upper right')
    ax1.set_ylim(0, 5)
    
    # Групповая задержка Баттерворта
    ax2 = axes[1]
    for n, color in zip(orders, colors):
        b, a = butter(n, 1, analog=True)
        w, h = freqs(b, a, omega)
        
        phi = np.unwrap(np.angle(h))
        group_delay = -np.gradient(phi, omega)
        
        ax2.semilogx(omega, group_delay, color=color, linewidth=2,
                     label=f'Баттерворта, n = {n}')
    
    ax2.set_xlabel('Частота ω, рад/с')
    ax2.set_ylabel('Групповая задержка τ, с')
    ax2.set_title('Фильтры Баттерворта')
    ax2.grid(True, linestyle='--', alpha=0.7)
    ax2.legend(loc='upper right')
    ax2.set_ylim(0, 5)
    
    # Групповая задержка Чебышева I типа
    ax3 = axes[2]
    rp = 1  # пульсации в полосе пропускания, дБ
    for n, color in zip(orders, colors):
        b, a = cheby1(n, rp, 1, analog=True)
        w, h = freqs(b, a, omega)
        
        phi = np.unwrap(np.angle(h))
        group_delay = -np.gradient(phi, omega)
        
        ax3.semilogx(omega, group_delay, color=color, linewidth=2,
                     label=f'Чебышева, n = {n}')
    
    ax3.set_xlabel('Частота ω, рад/с')
    ax3.set_ylabel('Групповая задержка τ, с')
    ax3.set_title('Фильтры Чебышева I типа')
    ax3.grid(True, linestyle='--', alpha=0.7)
    ax3.legend(loc='upper right')
    ax3.set_ylim(0, 5)
    
    plt.suptitle('Сравнение групповой задержки: Бесселя, Баттерворта и Чебышева')
    plt.tight_layout()
    plt.show()
    
    print("\nВыводы:")
    print("- У фильтров Бесселя групповая задержка максимально плоская в полосе пропускания")
    print("- У фильтров Баттерворта групповая задержка начинает расти на средних частотах")
    print("- У фильтров Чебышева групповая задержка имеет наихудшую равномерность с резкими всплесками")
    print("- Это делает фильтры Бесселя предпочтительными для задач, где требуется сохранение формы сигнала")


if __name__ == "__main__":
    compare_group_delay()
