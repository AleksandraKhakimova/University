import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D

def analyt_func(x, a, b, t):
    """Аналитическое решение"""
    return np.exp(-a * t) * np.cos(x + b * t)

def func_border1(a, b, t):
    """Граничное условие при x=0"""
    return -np.exp(-a * t) * (np.cos(b * t) + np.sin(b * t))

def func_border2(a, b, t):
    """Граничное условие при x=π"""
    return np.exp(-a * t) * (np.cos(b * t) + np.sin(b * t))

def run_through(a_coef, b_coef, c_coef, d_coef, s):
    """Метод прогонки (Thomas algorithm)"""
    P = np.zeros(s + 1)
    Q = np.zeros(s + 1)

    P[0] = -c_coef[0] / b_coef[0]
    Q[0] = d_coef[0] / b_coef[0]
    
    k = s - 1
    for i in range(1, s):
        P[i] = -c_coef[i] / (b_coef[i] + a_coef[i] * P[i - 1])
        Q[i] = (d_coef[i] - a_coef[i] * Q[i - 1]) / (b_coef[i] + a_coef[i] * P[i - 1])
    
    P[k] = 0
    Q[k] = (d_coef[k] - a_coef[k] * Q[k - 1]) / (b_coef[k] + a_coef[k] * P[k - 1])

    x = np.zeros(s)
    x[k] = Q[k]

    for i in range(s - 2, -1, -1):
        x[i] = P[i] * x[i + 1] + Q[i]

    return x

def explicit(K, t, tau, h, a, b, x, approx):
    """Явная конечно-разностная схема"""
    N = len(x)
    U = np.zeros((K, N))
    
    # Начальное условие
    for j in range(N):
        U[0, j] = np.cos(x[j])
    
    # Коэффициент Куранта для проверки устойчивости
    C = a * tau / h**2
    
    for k in range(K - 1):
        current_t = t + (k + 1) * tau
        
        # Внутренние точки
        for j in range(1, N - 1):
            U[k + 1, j] = (U[k, j] + 
                          C * (U[k, j - 1] - 2 * U[k, j] + U[k, j + 1]) +
                          (b * tau / (2 * h)) * (U[k, j + 1] - U[k, j - 1]))
        
        # Граничные условия
        if approx == 1:
            # Двухточечная аппроксимация с первым порядком
            U[k + 1, 0] = (h * func_border1(a, b, current_t) + U[k + 1, 1]) / (1 + h)
            U[k + 1, N - 1] = (h * func_border2(a, b, current_t) + U[k + 1, N - 2]) / (1 + h)
            
        elif approx == 2:
            # Трехточечная аппроксимация со вторым порядком
            U[k + 1, 0] = (2 * h * func_border1(a, b, current_t) - 4 * U[k + 1, 1] + U[k + 1, 2]) / (2 * h - 3)
            U[k + 1, N - 1] = (2 * h * func_border2(a, b, current_t) + 4 * U[k + 1, N - 2] - U[k + 1, N - 3]) / (2 * h + 3)
            
        elif approx == 3:
            # Двухточечная аппроксимация со вторым порядком (из теории)
            denominator_left = -2 * tau - h**2 + h * tau * (2 - b * h)
            U[k + 1, 0] = (func_border1(a, b, current_t) * h * tau * (2 - b * h) - 
                          U[k + 1, 1] * (2 * tau) - U[k, 0] * h**2) / denominator_left
                          
            denominator_right = 2 * tau + h**2 + h * tau * (2 + b * h)
            U[k + 1, N - 1] = (func_border2(a, b, current_t) * h * tau * (2 + b * h) + 
                             U[k + 1, N - 2] * (2 * tau) + U[k, N - 1] * h**2) / denominator_right
    
    return U, C

def implicit(K, t, tau, h, a, b, x, approx):
    """Неявная конечно-разностная схема"""
    N = len(x)
    U = np.zeros((K, N))
    
    # Начальное условие
    for j in range(N):
        U[0, j] = np.cos(x[j])
    
    C = a * tau / h**2
    D = b * tau / (2 * h)
    
    for k in range(K - 1):
        current_t = t + (k + 1) * tau
        
        # Коэффициенты для внутренних точек
        a_coef = np.zeros(N)
        b_coef = np.zeros(N)
        c_coef = np.zeros(N)
        d_coef = np.zeros(N)
        
        for j in range(1, N - 1):
            a_coef[j] = -C + D
            b_coef[j] = 1 + 2 * C
            c_coef[j] = -C - D
            d_coef[j] = U[k, j]
        
        # Граничные условия
        if approx == 1:
            # Двухточечная аппроксимация с первым порядком
            b_coef[0] = -1 - 1/h
            c_coef[0] = 1/h
            d_coef[0] = func_border1(a, b, current_t)
            
            a_coef[N-1] = -1/h
            b_coef[N-1] = 1 + 1/h
            d_coef[N-1] = func_border2(a, b, current_t)
            
        elif approx == 2:
            # Трехточечная аппроксимация со вторым порядком
            b_coef[0] = -3/(2*h) - 1
            c_coef[0] = 2/h
            a_coef[0] = -1/(2*h)
            d_coef[0] = func_border1(a, b, current_t)
            
            a_coef[N-1] = 1/(2*h)
            b_coef[N-1] = 3/(2*h) - 1
            c_coef[N-1] = -2/h
            d_coef[N-1] = func_border2(a, b, current_t)
            
        elif approx == 3:
            # Двухточечная аппроксимация со вторым порядком (из теории)
            alpha, beta = 1, -1  # коэффициенты граничных условий
            
            # Левая граница
            b_coef[0] = (2*a)/h + h/tau - (beta/alpha)*(2*a - b*h)
            c_coef[0] = -(2*a)/h
            d_coef[0] = (h/tau) * U[k, 0] - func_border1(a, b, current_t) * (2*a - b*h)/alpha
            
            # Правая граница
            a_coef[N-1] = -(2*a)/h
            b_coef[N-1] = (2*a)/h + h/tau + (beta/alpha)*(2*a + b*h)
            d_coef[N-1] = (h/tau) * U[k, N-1] + func_border2(a, b, current_t) * (2*a + b*h)/alpha
        
        # Решение системы методом прогонки
        U[k + 1, :] = run_through(a_coef, b_coef, c_coef, d_coef, N)
    
    return U, C

def Krank_Nikolson(K, t, tau, h, a, b, x, approx, theta=0.5):
    """Схема Кранка-Николсона"""
    N = len(x)
    U = np.zeros((K, N))
    
    # Начальное условие
    for j in range(N):
        U[0, j] = np.cos(x[j])
    
    C = a * tau / (2 * h**2)  # коэффициент для полусуммы
    D = b * tau / (4 * h)     # коэффициент для полусуммы
    
    for k in range(K - 1):
        current_t = t + (k + 1) * tau
        
        # Коэффициенты для схемы Кранка-Николсона
        a_coef = np.zeros(N)
        b_coef = np.zeros(N)
        c_coef = np.zeros(N)
        d_coef = np.zeros(N)
        
        # Внутренние точки
        for j in range(1, N - 1):
            a_coef[j] = -C + D
            b_coef[j] = 1 + 2 * C
            c_coef[j] = -C - D
            
            # Правая часть (явная часть)
            d_coef[j] = (C - D) * U[k, j-1] + (1 - 2 * C) * U[k, j] + (C + D) * U[k, j+1]
        
        # Граничные условия (аналогично неявной схеме)
        if approx == 1:
            b_coef[0] = -1 - 1/h
            c_coef[0] = 1/h
            d_coef[0] = func_border1(a, b, current_t)
            
            a_coef[N-1] = -1/h
            b_coef[N-1] = 1 + 1/h
            d_coef[N-1] = func_border2(a, b, current_t)
            
        elif approx == 2:
            b_coef[0] = -3/(2*h) - 1
            c_coef[0] = 2/h
            a_coef[0] = -1/(2*h)
            d_coef[0] = func_border1(a, b, current_t)
            
            a_coef[N-1] = 1/(2*h)
            b_coef[N-1] = 3/(2*h) - 1
            c_coef[N-1] = -2/h
            d_coef[N-1] = func_border2(a, b, current_t)
            
        elif approx == 3:
            alpha, beta = 1, -1
            
            b_coef[0] = (2*a)/h + h/tau - (beta/alpha)*(2*a - b*h)
            c_coef[0] = -(2*a)/h
            d_coef[0] = (h/tau) * U[k, 0] - func_border1(a, b, current_t) * (2*a - b*h)/alpha
            
            a_coef[N-1] = -(2*a)/h
            b_coef[N-1] = (2*a)/h + h/tau + (beta/alpha)*(2*a + b*h)
            d_coef[N-1] = (h/tau) * U[k, N-1] + func_border2(a, b, current_t) * (2*a + b*h)/alpha
        
        # Решение системы
        U[k + 1, :] = run_through(a_coef, b_coef, c_coef, d_coef, N)
    
    return U, C

def calculate_errors(U, x, T, a, b):
    """Вычисление погрешностей численного решения"""
    errors = {}
    
    # Погрешность в различные моменты времени
    time_indices = [0, len(T)//4, len(T)//2, 3*len(T)//4, -1]
    for idx in time_indices:
        if idx < len(U):
            U_analytic = analyt_func(x, a, b, T[idx])
            error = np.abs(U_analytic - U[idx, :])
            errors[f't_{idx}'] = {
                'max_error': np.max(error),
                'mean_error': np.mean(error),
                'time': T[idx]
            }
    
    # Общая погрешность по времени
    max_errors_over_time = []
    for k in range(len(U)):
        U_analytic = analyt_func(x, a, b, T[k])
        error = np.abs(U_analytic - U[k, :])
        max_errors_over_time.append(np.max(error))
    
    errors['over_time'] = max_errors_over_time
    
    return errors

def plot_results(x, T, U, errors, a, b, method_name, approx_name):
    """Визуализация результатов"""
    
    # 1. Сравнение в выбранный момент времени
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # График решения в последний момент времени
    U_analytic = analyt_func(x, a, b, T[-1])
    axes[0, 0].plot(x, U_analytic, 'r-', linewidth=2, label='Аналитическое решение')
    axes[0, 0].plot(x, U[-1, :], 'bo-', markersize=3, label=f'Численное ({method_name})')
    axes[0, 0].set_xlabel('x')
    axes[0, 0].set_ylabel('u(x,t)')
    axes[0, 0].set_title(f'Решение в момент t = {T[-1]:.3f}\n{approx_name}')
    axes[0, 0].legend()
    axes[0, 0].grid(True)
    
    # График погрешности в последний момент времени
    error = np.abs(U_analytic - U[-1, :])
    axes[0, 1].plot(x, error, 'g-', linewidth=2)
    axes[0, 1].set_xlabel('x')
    axes[0, 1].set_ylabel('Абсолютная погрешность')
    axes[0, 1].set_title(f'Погрешность в момент t = {T[-1]:.3f}\nМакс. погр.: {np.max(error):.2e}')
    axes[0, 1].grid(True)
    
    # Зависимость максимальной погрешности от времени
    axes[1, 0].plot(T, errors['over_time'], 'b-', linewidth=2)
    axes[1, 0].set_xlabel('Время t')
    axes[1, 0].set_ylabel('Максимальная погрешность')
    axes[1, 0].set_title('Зависимость погрешности от времени')
    axes[1, 0].grid(True)
    axes[1, 0].set_yscale('log')
    
    # 3D график численного решения
    X, T_mesh = np.meshgrid(x, T)
    ax_3d = fig.add_subplot(2, 2, 4, projection='3d')
    surf = ax_3d.plot_surface(X, T_mesh, U, cmap='viridis', alpha=0.8)
    ax_3d.set_xlabel('x')
    ax_3d.set_ylabel('t')
    ax_3d.set_zlabel('u(x,t)')
    ax_3d.set_title('Численное решение u(x,t)')
    
    plt.tight_layout()
    plt.show()
    
    # Вывод информации о погрешностях
    print(f"\n{method_name} - {approx_name}")
    print("=" * 50)
    for key, value in errors.items():
        if key != 'over_time':
            print(f"Время t = {value['time']:.3f}:")
            print(f"  Макс. погрешность: {value['max_error']:.2e}")
            print(f"  Средняя погрешность: {value['mean_error']:.2e}")

def convergence_study(a, b, time, approx):
    """Исследование сходимости при различных сеточных параметрах"""
    N_values = [20, 40, 80, 160]
    K_values = [500, 1000, 2000, 4000]
    
    errors_N = []
    errors_K = []
    
    # Исследование сходимости по пространству
    K_fixed = 2000
    for N in N_values:
        h = np.pi / N
        tau = time / K_fixed
        x = np.linspace(0, np.pi, N + 1)
        T = np.linspace(0, time, K_fixed)
        
        U, _ = implicit(K_fixed, 0, tau, h, a, b, x, approx)
        U_analytic = analyt_func(x, a, b, T[-1])
        error = np.max(np.abs(U_analytic - U[-1, :]))
        errors_N.append(error)
    
    # Исследование сходимости по времени
    N_fixed = 100
    for K in K_values:
        h = np.pi / N_fixed
        tau = time / K
        x = np.linspace(0, np.pi, N_fixed + 1)
        T = np.linspace(0, time, K)
        
        U, _ = implicit(K, 0, tau, h, a, b, x, approx)
        U_analytic = analyt_func(x, a, b, T[-1])
        error = np.max(np.abs(U_analytic - U[-1, :]))
        errors_K.append(error)
    
    # Графики сходимости
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    axes[0].loglog(N_values, errors_N, 'bo-', label='Погрешность')
    axes[0].loglog(N_values, [1/n**2 for n in N_values], 'r--', label='O(h²)')
    axes[0].set_xlabel('N (количество узлов по пространству)')
    axes[0].set_ylabel('Максимальная погрешность')
    axes[0].set_title('Сходимость по пространству')
    axes[0].legend()
    axes[0].grid(True)
    
    axes[1].loglog(K_values, errors_K, 'bo-', label='Погрешность')
    axes[1].loglog(K_values, [1/k for k in K_values], 'r--', label='O(τ)')
    axes[1].set_xlabel('K (количество шагов по времени)')
    axes[1].set_ylabel('Максимальная погрешность')
    axes[1].set_title('Сходимость по времени')
    axes[1].legend()
    axes[1].grid(True)
    
    plt.tight_layout()
    plt.show()

def main():
    """Основная функция"""
    # Параметры задачи
    a = 1.0  # a > 0
    b = 1.0  # b > 0
    time = 2.0  # Общее время моделирования
    
    # Сеточные параметры
    N = 50    # Узлы по пространству
    K = 1000  # Шаги по времени
    
    h = np.pi / N
    tau = time / K
    x = np.linspace(0, np.pi, N + 1)
    T = np.linspace(0, time, K)
    
    method_names = {
        1: "Явная схема",
        2: "Неявная схема", 
        3: "Схема Кранка-Николсона"
    }
    
    approx_names = {
        1: "Двухточечная аппроксимация (1-й порядок)",
        2: "Трехточечная аппроксимация (2-й порядок)",
        3: "Двухточечная аппроксимация (2-й порядок, теория)"
    }
    
    while True:
        print("\n" + "="*60)
        print("ЧИСЛЕННОЕ РЕШЕНИЕ ПАРАБОЛИЧЕСКОГО УРАВНЕНИЯ")
        print("="*60)
        
        print("Выберите метод:")
        print("1 - Явная конечно-разностная схема")
        print("2 - Неявная конечно-разностная схема") 
        print("3 - Схема Кранка-Николсона")
        print("4 - Исследование сходимости")
        print("0 - Выход")
        
        choice = int(input("Ваш выбор: "))
        
        if choice == 0:
            break
            
        elif choice == 4:
            approx = int(input("Выберите аппроксимацию (1, 2, 3): "))
            convergence_study(a, b, time, approx)
            continue
        
        elif choice in [1, 2, 3]:
            print("Выберите аппроксимацию граничных условий:")
            print("1 - Двухточечная с первым порядком")
            print("2 - Трехточечная со вторым порядком") 
            print("3 - Двухточечная со вторым порядком (из теории)")
            
            approx = int(input("Ваш выбор: "))
            
            if choice == 1:
                U, C = explicit(K, 0, tau, h, a, b, x, approx)
                if C > 0.5:
                    print(f"ВНИМАНИЕ: Условие Куранта не выполнено (C = {C:.3f} > 0.5)")
            elif choice == 2:
                U, C = implicit(K, 0, tau, h, a, b, x, approx)
            elif choice == 3:
                theta = float(input("Введите параметр theta (0-1, 0.5 для чистой схемы): "))
                U, C = Krank_Nikolson(K, 0, tau, h, a, b, x, approx, theta)
            
            # Вычисление погрешностей
            errors = calculate_errors(U, x, T, a, b)
            1
            
            # Визуализация результатов
            plot_results(x, T, U, errors, a, b, 
                        method_names[choice], approx_names[approx])
            
            # Дополнительный анализ
            print(f"\nКоэффициент Куранта: C = {C:.6f}")
            print(f"Шаг по пространству: h = {h:.6f}")
            print(f"Шаг по времени: τ = {tau:.6f}")
        
        else:
            print("Неверный выбор!")
    
    print("Программа завершена.")

if __name__ == "__main__":
    main()
