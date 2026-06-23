import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d
import time

def analyt_func(mu, X, Y, t):
    return np.sin(X) * np.sin(Y) * np.sin(mu * t)

def func(a, b, mu, x, y, t):
    return np.sin(x) * np.sin(y) * (mu * np.cos(mu * t) + (a + b) * np.sin(mu * t))

def func_border1(mu, y, t):
    return 0

def func_border2(mu, y, t):
    return np.sin(y) * np.sin(mu * t)

def func_border3(mu, x, t):
    return 0

def func_border4(mu, x, t):
    return -np.sin(x) * np.sin(mu * t)

def norm(U1, U2):
    return np.max(np.abs(U1 - U2))

def run_through(a, b, c, d, s):
    P = np.zeros(s)
    Q = np.zeros(s)
    
    P[0] = -c[0] / b[0]
    Q[0] = d[0] / b[0]
    
    for i in range(1, s):
        denominator = b[i] + a[i] * P[i-1]
        P[i] = -c[i] / denominator
        Q[i] = (d[i] - a[i] * Q[i-1]) / denominator
    
    x = np.zeros(s)
    x[s-1] = Q[s-1]
    
    for i in range(s-2, -1, -1):
        x[i] = P[i] * x[i+1] + Q[i]
    
    return x

def variable_directions(a1, b1, mu, x, y, hx, hy, K, tau):
    Nx = len(x)
    Ny = len(y)
    U = np.zeros((K, Nx, Ny))
    
    sigma_a = (a1 * tau) / (2 * hx**2)
    sigma_b = (b1 * tau) / (2 * hy**2)

    for k in range(1, K):
        t_half = (k - 0.5) * tau
        t_full = k * tau
        
        U_temp = np.zeros((Nx, Ny))
        
        # Первый полуслой (по x)
        for j in range(1, Ny-1):
            a = np.zeros(Nx)
            b = np.zeros(Nx)
            c = np.zeros(Nx)
            d = np.zeros(Nx)
            
            for i in range(1, Nx-1):
                a[i] = -sigma_a
                b[i] = 1 + 2 * sigma_a
                c[i] = -sigma_a
                d[i] = sigma_b * (U[k-1, i, j+1] - 2 * U[k-1, i, j] + U[k-1, i, j-1]) + \
                       (tau/2) * func(a1, b1, mu, x[i], y[j], t_half) + U[k-1, i, j]
            
            # Граничные условия по x
            b[0] = 1
            c[0] = 0
            d[0] = func_border1(mu, y[j], t_half)
            
            a[-1] = 0
            b[-1] = 1
            d[-1] = func_border2(mu, y[j], t_half)
            
            solution = run_through(a, b, c, d, Nx)
            U_temp[:, j] = solution
        
        # Граничные условия по y для промежуточного решения
        for i in range(Nx):
            U_temp[i, 0] = func_border3(mu, x[i], t_half)
            # Условие Неймана
            U_temp[i, -1] = U_temp[i, -2] + hy * func_border4(mu, x[i], t_half)
        
        # Второй полуслой (по y)
        for i in range(1, Nx-1):
            a = np.zeros(Ny)
            b = np.zeros(Ny)
            c = np.zeros(Ny)
            d = np.zeros(Ny)
            
            for j in range(1, Ny-1):
                a[j] = -sigma_b
                b[j] = 1 + 2 * sigma_b
                c[j] = -sigma_b
                d[j] = sigma_a * (U_temp[i+1, j] - 2 * U_temp[i, j] + U_temp[i-1, j]) + \
                       (tau/2) * func(a1, b1, mu, x[i], y[j], t_full) + U_temp[i, j]
            
            # Граничные условия по y
            b[0] = 1
            c[0] = 0
            d[0] = func_border3(mu, x[i], t_full)
            
            a[-1] = -1
            b[-1] = 1
            d[-1] = hy * func_border4(mu, x[i], t_full)
            
            solution = run_through(a, b, c, d, Ny)
            U[k, i, :] = solution
        
        # Граничные условия по x для финального решения
        for j in range(Ny):
            U[k, 0, j] = func_border1(mu, y[j], t_full)
            U[k, -1, j] = func_border2(mu, y[j], t_full)

    return U

def fractional_step(a1, b1, mu, x, y, hx, hy, K, tau):
    Nx = len(x)
    Ny = len(y)
    U = np.zeros((K, Nx, Ny))
    
    sigma_a = (a1 * tau) / hx**2
    sigma_b = (b1 * tau) / hy**2

    for k in range(1, K):
        t_half = (k - 0.5) * tau
        t_full = k * tau
        
        U_temp = np.zeros((Nx, Ny))
        
        # Первый шаг (по x)
        for j in range(1, Ny-1):
            a = np.zeros(Nx)
            b = np.zeros(Nx)
            c = np.zeros(Nx)
            d = np.zeros(Nx)
            
            for i in range(1, Nx-1):
                a[i] = -sigma_a
                b[i] = 1 + 2 * sigma_a
                c[i] = -sigma_a
                d[i] = (tau/2) * func(a1, b1, mu, x[i], y[j], t_half) + U[k-1, i, j]
            
            # Граничные условия по x
            b[0] = 1
            c[0] = 0
            d[0] = func_border1(mu, y[j], t_half)
            
            a[-1] = 0
            b[-1] = 1
            d[-1] = func_border2(mu, y[j], t_half)
            
            solution = run_through(a, b, c, d, Nx)
            U_temp[:, j] = solution
        
        # Граничные условия по y для промежуточного решения
        for i in range(Nx):
            U_temp[i, 0] = func_border3(mu, x[i], t_half)
            # Условие Неймана
            U_temp[i, -1] = U_temp[i, -2] + hy * func_border4(mu, x[i], t_half)
        
        # Второй шаг (по y)
        for i in range(1, Nx-1):
            a = np.zeros(Ny)
            b = np.zeros(Ny)
            c = np.zeros(Ny)
            d = np.zeros(Ny)
            
            for j in range(1, Ny-1):
                a[j] = -sigma_b
                b[j] = 1 + 2 * sigma_b
                c[j] = -sigma_b
                d[j] = (tau/2) * func(a1, b1, mu, x[i], y[j], t_full) + U_temp[i, j]
            
            # Граничные условия по y
            b[0] = 1
            c[0] = 0
            d[0] = func_border3(mu, x[i], t_full)
            
            a[-1] = -1
            b[-1] = 1
            d[-1] = hy * func_border4(mu, x[i], t_full)
            
            solution = run_through(a, b, c, d, Ny)
            U[k, i, :] = solution
        
        # Граничные условия по x для финального решения
        for j in range(Ny):
            U[k, 0, j] = func_border1(mu, y[j], t_full)
            U[k, -1, j] = func_border2(mu, y[j], t_full)

    return U

def compare_methods(Nx, Ny, K, time_total, a, b, mu):
    """Сравнение двух методов"""
    
    # Сетка
    hx = (np.pi/2 - 0) / Nx
    hy = (np.pi - 0) / Ny
    x = np.linspace(0, np.pi/2, Nx)
    y = np.linspace(0, np.pi, Ny)
    tau = time_total / K
    T = np.linspace(0, time_total, K)
    
    # Создаем сетку для аналитического решения
    X, Y = np.meshgrid(x, y, indexing='ij')
    
    print(f"Сравнение методов для a={a}, b={b}, μ={mu}")
    print(f"Сетка: {Nx}x{Ny}, Время: {time_total}, Шагов: {K}")
    
    # Замер времени для ADI
    print("Запуск ADI метода...")
    start_time = time.time()
    U_adi = variable_directions(a, b, mu, x, y, hx, hy, K, tau)
    time_adi = time.time() - start_time
    
    # Замер времени для дробных шагов
    print("Запуск метода дробных шагов...")
    start_time = time.time()
    U_frac = fractional_step(a, b, mu, x, y, hx, hy, K, tau)
    time_frac = time.time() - start_time
    
    # Вычисление ошибок
    print("Вычисление ошибок...")
    errors_adi = []
    errors_frac = []
    
    for k in range(K):
        U_anal = analyt_func(mu, X, Y, T[k])
        errors_adi.append(norm(U_anal, U_adi[k, :, :]))
        errors_frac.append(norm(U_anal, U_frac[k, :, :]))
    
    # Результаты
    print(f"\nРЕЗУЛЬТАТЫ:")
    print(f"Метод переменных направлений:")
    print(f"  - Время выполнения: {time_adi:.3f} сек")
    print(f"  - Макс. ошибка: {max(errors_adi):.6f}")
    print(f"  - Средняя ошибка: {np.mean(errors_adi):.6f}")
    
    print(f"Метод дробных шагов:")
    print(f"  - Время выполнения: {time_frac:.3f} сек") 
    print(f"  - Макс. ошибка: {max(errors_frac):.6f}")
    print(f"  - Средняя ошибка: {np.mean(errors_frac):.6f}")
    
    # Построение графиков сравнения
    print("Построение графиков...")
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle(f'Сравнение методов: a={a}, b={b}, μ={mu}', fontsize=16)
    
    # График ошибок по времени
    axes[0,0].plot(T, errors_adi, 'r-', linewidth=2, label='ADI (перем. направлений)')
    axes[0,0].plot(T, errors_frac, 'b-', linewidth=2, label='Дробные шаги')
    axes[0,0].set_xlabel('Время t')
    axes[0,0].set_ylabel('Максимальная ошибка')
    axes[0,0].set_title('Ошибки методов по времени')
    axes[0,0].legend()
    axes[0,0].grid(True)
    
    # График отношения ошибок
    with np.errstate(divide='ignore', invalid='ignore'):
        ratio = np.array(errors_frac) / np.array(errors_adi)
        ratio = np.nan_to_num(ratio, nan=1.0, posinf=1.0, neginf=1.0)
    
    axes[0,1].plot(T, ratio, 'g-', linewidth=2)
    axes[0,1].axhline(y=1, color='k', linestyle='--', alpha=0.5)
    axes[0,1].set_xlabel('Время t')
    axes[0,1].set_ylabel('Ошибка(дробные) / Ошибка(ADI)')
    axes[0,1].set_title('Отношение ошибок методов')
    axes[0,1].grid(True)
    
    # Столбчатая диаграмма характеристик
    methods = ['ADI', 'Дробные\nшаги']
    times = [time_adi, time_frac]
    max_errors = [max(errors_adi), max(errors_frac)]
    
    x_pos = np.arange(len(methods))
    axes[0,2].bar(x_pos - 0.2, times, 0.4, label='Время (сек)', alpha=0.7, color='orange')
    axes[0,2].bar(x_pos + 0.2, max_errors, 0.4, label='Макс. ошибка', alpha=0.7, color='red')
    axes[0,2].set_xticks(x_pos)
    axes[0,2].set_xticklabels(methods)
    axes[0,2].set_ylabel('Значения')
    axes[0,2].set_title('Сравнение производительности')
    axes[0,2].legend()
    axes[0,2].grid(True, alpha=0.3)
    
    # Решения в последний момент времени
    dt = K - 1
    U_anal_final = analyt_func(mu, X, Y, T[dt])
    
    # ADI решение
    im1 = axes[1,0].contourf(X, Y, U_adi[dt, :, :], levels=50, cmap='viridis')
    axes[1,0].set_xlabel('x')
    axes[1,0].set_ylabel('y')
    axes[1,0].set_title('ADI метод (последний момент)')
    plt.colorbar(im1, ax=axes[1,0])
    
    # Дробные шаги решение
    im2 = axes[1,1].contourf(X, Y, U_frac[dt, :, :], levels=50, cmap='viridis')
    axes[1,1].set_xlabel('x')
    axes[1,1].set_ylabel('y')
    axes[1,1].set_title('Дробные шаги (последний момент)')
    plt.colorbar(im2, ax=axes[1,1])
    
    # Разность методов
    diff = U_adi[dt, :, :] - U_frac[dt, :, :]
    im3 = axes[1,2].contourf(X, Y, diff, levels=50, cmap='RdBu_r')
    axes[1,2].set_xlabel('x')
    axes[1,2].set_ylabel('y')
    axes[1,2].set_title('Разность ADI - Дробные шаги')
    plt.colorbar(im3, ax=axes[1,2])
    
    plt.tight_layout()
    plt.show()
    
    return {
        'time_adi': time_adi,
        'time_frac': time_frac,
        'max_error_adi': max(errors_adi),
        'max_error_frac': max(errors_frac),
        'mean_error_adi': np.mean(errors_adi),
        'mean_error_frac': np.mean(errors_frac)
    }

def main_comparison():
    """Основная функция сравнения"""
    
    # Уменьшим параметры для быстрого тестирования
    Nx = 20
    Ny = 20
    K = 50
    time_total = 1.0
    
    # Тестируем одну комбинацию параметров для начала
    print("Запуск сравнения методов...")
    
    results = compare_methods(Nx, Ny, K, time_total, a=1, b=1, mu=1)
    
    # Сводная таблица результатов
    print(f"\n{'='*60}")
    print("СВОДНАЯ ТАБЛИЦА РЕЗУЛЬТАТОВ")
    print(f"{'='*60}")
    
    print(f"{'Метод':<20} {'Время (сек)':<12} {'Макс. ошибка':<15} {'Ср. ошибка':<12}")
    print(f"{'-'*60}")
    
    res = results
    print(f"{'ADI':<20} {res['time_adi']:<12.3f} {res['max_error_adi']:<15.6f} {res['mean_error_adi']:<12.6f}")
    print(f"{'Дробные шаги':<20} {res['time_frac']:<12.3f} {res['max_error_frac']:<15.6f} {res['mean_error_frac']:<12.6f}")

# Запуск сравнения
if __name__ == "__main__":
    main_comparison()