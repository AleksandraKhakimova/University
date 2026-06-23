import numpy as np
import matplotlib.pyplot as plt

def analyt_func(x, t):
    """Аналитическое решение"""
    return np.exp(-t) * np.cos(x)

def func(x, t):
    """Функция правой части уравнения (неоднородность)"""
    return np.sin(x) * np.exp(-t)

def func_border1(t):
    """Левое граничное условие при x=0"""
    return np.exp(-t)

def func_border2(t):
    """Правое граничное условие при x=π"""
    return -np.exp(-t)

def run_through(a, b, c, d, s):
    """Метод прогонки для решения трехдиагональных систем для неявной схемы"""
    P = np.zeros(s + 1)
    Q = np.zeros(s + 1)

    # Прямой ход (строится матрица)
    P[0] = -c[0] / b[0]
    Q[0] = d[0] / b[0]

    k = s - 1
    for i in range(1, s):
        P[i] = -c[i] / (b[i] + a[i] * P[i - 1])
        Q[i] = (d[i] - a[i] * Q[i - 1]) / (b[i] + a[i] * P[i - 1])
    
    P[k] = 0
    Q[k] = (d[k] - a[k] * Q[k - 1]) / (b[k] + a[k] * P[k - 1])

    # Обратный ход
    x = np.zeros(s)
    x[k] = Q[k]

    for i in range(s - 2, -1, -1):
        x[i] = P[i] * x[i + 1] + Q[i]

    return x

def explicit(K, t, tau, h, x, approx_st, approx_bo):
    """Явная конечно-разностная схема"""
    N = len(x)
    U = np.zeros((K, N))
    
    # Начальные условия
    for j in range(N):
        U[0, j] = np.cos(x[j])  # u(x,0) = cos(x)
        
        # Аппроксимация начальной скорости u_t(x,0) = -cos(x)
        if approx_st == 1:
            # Первый порядок: u_t(x,0) ≈ (U[1,j] - U[0,j])/τ = -cos(x)
            U[1][j] = np.cos(x[j]) - np.cos(x[j]) * tau
        elif approx_st == 2:
            # Второй порядок с использованием уравнения
            # Из уравнения: u_tt(x,0) = u_xx(x,0) + u_x(x,0) - u(x,0) + sin(x) - 3u_t(x,0)
            u_xx = -np.cos(x[j])  # вторая производная cos(x)
            u_x = -np.sin(x[j])   # первая производная cos(x)
            u_tt = u_xx + u_x - np.cos(x[j]) + np.sin(x[j]) - 3 * (-np.cos(x[j]))
            U[1][j] = np.cos(x[j]) - np.cos(x[j]) * tau + 0.5 * u_tt * tau**2

    # Основной цикл по времени
    for k in range(1, K - 1):
        t += tau
        for j in range(1, N - 1):
            # Явная схема для уравнения: u_tt + 3u_t = u_xx + u_x - u + sin(x)exp(-t)
            U[k + 1, j] = (tau**2 * ((U[k, j + 1] - 2 * U[k, j] + U[k, j - 1]) / h**2 + 
                                    (U[k, j + 1] - U[k, j - 1]) / (2 * h) - 
                                    U[k, j] + func(x[j], t)) +
                           (2 + 3 * tau) * U[k, j] - U[k - 1, j]) / (1 + 3 * tau)
        
        # Граничные условия
        if approx_bo == 1:
            # Двухточечная аппроксимация с первым порядком
            U[k + 1, 0] = func_border1(t)  # u(0,t) = exp(-t)
            U[k + 1, N - 1] = func_border2(t)  # u(π,t) = -exp(-t)
            
        elif approx_bo == 2:
            # Трехточечная аппроксимация со вторым порядком
            U[k + 1, 0] = func_border1(t)
            # Используем трехточечный шаблон для правой границы
            U[k + 1, N - 1] = (4 * U[k + 1, N - 2] - U[k + 1, N - 3] - 
                              2 * h * func_border2(t)) / 3
            
        elif approx_bo == 3:
            # Двухточечная аппроксимация со вторым порядком
            U[k + 1, 0] = func_border1(t)
            U[k + 1, N - 1] = (4 * U[k + 1, N - 2] - U[k + 1, N - 3]) / 3

    return U

def implicit(K, t, tau, h, x, approx_st, approx_bo):
    """Неявная конечно-разностная схема"""
    N = len(x)
    U = np.zeros((K, N))
    
    # Начальные условия
    for j in range(N):
        U[0, j] = np.cos(x[j])  # u(x,0) = cos(x)
        
        # Аппроксимация начальной скорости u_t(x,0) = -cos(x)
        if approx_st == 1:
            U[1][j] = np.cos(x[j]) - np.cos(x[j]) * tau
        elif approx_st == 2:
            u_xx = -np.cos(x[j])
            u_x = -np.sin(x[j])
            u_tt = u_xx + u_x - np.cos(x[j]) + np.sin(x[j]) - 3 * (-np.cos(x[j]))
            U[1][j] = np.cos(x[j]) - np.cos(x[j]) * tau + 0.5 * u_tt * tau**2

    # Основной цикл по времени
    for k in range(1, K - 1):
        a = np.zeros(N)
        b = np.zeros(N)
        c = np.zeros(N)
        d = np.zeros(N)
        t += tau

        # Коэффициенты для внутренних точек (для построение матрицы)
        for j in range(1, N - 1):
            a[j] = tau**2 / h**2 - tau**2 / (2 * h)      # Коэффициент при U[j-1]
            b[j] = -2 * tau**2 / h**2 - tau**2 - 1 - 3 * tau  # Коэффициент при U[j]
            c[j] = tau**2 / h**2 + tau**2 / (2 * h)      # Коэффициент при U[j+1]
            d[j] = tau**2 * func(x[j], t) - (2 + 3 * tau) * U[k, j] + U[k - 1, j]
        
        # Граничные условия
        if approx_bo == 1:
            # Двухточечная аппроксимация с первым порядком
            b[0] = 1
            c[0] = 0
            d[0] = func_border1(t)

            a[N - 1] = 0
            b[N - 1] = 1
            d[N - 1] = func_border2(t)
            
        elif approx_bo == 2:
            # Трехточечная аппроксимация со вторым порядком
            b[0] = 1
            c[0] = 0
            d[0] = func_border1(t)

            # Для правой границы: трехточечная аппроксимация
            a[N - 1] = 1
            b[N - 1] = -4
            c[N - 1] = 3
            d[N - 1] = 2 * h * func_border2(t)
            
        elif approx_bo == 3:
            # Двухточечная аппроксимация со вторым порядком
            b[0] = 1
            c[0] = 0
            d[0] = func_border1(t)

            a[N - 1] = 1
            b[N - 1] = -1
            c[N - 1] = 0
            d[N - 1] = h * func_border2(t)

        # Решение системы методом прогонки
        u_new = run_through(a, b, c, d, N)
        for i in range(N):
            U[k + 1, i] = u_new[i]   
                 
    return U

def research_convergence(time=1.0):
    """Исследование зависимости погрешности от сеточных параметров"""
    print("\n=== ИССЛЕДОВАНИЕ СХОДИМОСТИ ===")
    
    # Различные значения параметров сетки
    N_values = [20, 40, 80, 160]  # различные h
    K_values = [500, 1000, 2000, 4000]  # различные τ
    
    errors_h = []
    errors_tau = []
    
    # Исследование зависимости от h (фиксируем τ)
    print("Исследование зависимости от h (фиксированный τ):")
    fixed_K = 2000
    fixed_tau = time / fixed_K
    
    for N in N_values:
        h = np.pi / N
        x = np.arange(0, np.pi + h/2, h)
        
        # Вычисление решения (явная схема, аппроксимация 2-го порядка)
        U = explicit(fixed_K, 0, fixed_tau, h, x, 2, 1)
        
        # Вычисление максимальной ошибки в последний момент времени
        U_analytic = analyt_func(x, time)
        max_error = np.max(np.abs(U_analytic - U[-1, :]))
        errors_h.append((h, max_error))
        print(f"h = {h:.6f}, N = {N}, ошибка = {max_error:.6f}")
    
    # Исследование зависимости от τ (фиксируем h)
    print("\nИсследование зависимости от τ (фиксированный h):")
    fixed_N = 100
    fixed_h = np.pi / fixed_N
    x = np.arange(0, np.pi + fixed_h/2, fixed_h)
    
    for K in K_values:
        tau = time / K
        
        # Вычисление решения (явная схема, аппроксимация 2-го порядка)
        U = explicit(K, 0, tau, fixed_h, x, 2, 1)
        
        # Вычисление максимальной ошибки в последний момент времени
        U_analytic = analyt_func(x, time)
        max_error = np.max(np.abs(U_analytic - U[-1, :]))
        errors_tau.append((tau, max_error))
        print(f"τ = {tau:.6f}, K = {K}, ошибка = {max_error:.6f}")
    
    # Построение графиков сходимости
    plt.figure(figsize=(12, 5))
    
    # График зависимости от h
    plt.subplot(1, 2, 1)
    h_vals = [e[0] for e in errors_h]
    error_vals = [e[1] for e in errors_h]
    plt.loglog(h_vals, error_vals, 'o-', label='Ошибка')
    plt.loglog(h_vals, [e*10 for e in h_vals], '--', label='O(h)')
    plt.loglog(h_vals, [e**2*10 for e in h_vals], '--', label='O(h²)')
    plt.xlabel('Шаг по пространству h')
    plt.ylabel('Максимальная ошибка')
    plt.title('Зависимость ошибки от h')
    plt.grid(True)
    plt.legend()
    
    # График зависимости от τ
    plt.subplot(1, 2, 2)
    tau_vals = [e[0] for e in errors_tau]
    error_vals = [e[1] for e in errors_tau]
    plt.loglog(tau_vals, error_vals, 'o-', label='Ошибка')
    plt.loglog(tau_vals, [e*10 for e in tau_vals], '--', label='O(τ)')
    plt.loglog(tau_vals, [e**2*100 for e in tau_vals], '--', label='O(τ²)')
    plt.xlabel('Шаг по времени τ')
    plt.ylabel('Максимальная ошибка')
    plt.title('Зависимость ошибки от τ')
    plt.grid(True)
    plt.legend()
    
    plt.tight_layout()
    plt.show()
    
    return errors_h, errors_tau

def main(N, K, time):
    """Основная функция программы"""
    # Параметры сетки
    h = np.pi / N  # шаг по пространству
    tau = time / K  # шаг по времени
    x = np.arange(0, np.pi + h / 2 - 1e-4, h)  # пространственная сетка
    T = np.arange(0, time + tau/2, tau)  # временная сетка
    
    print(f"Параметры сетки: N={N}, K={K}, h={h:.6f}, τ={tau:.6f}")
    print(f"Область: x∈[0, π], t∈[0, {time}]")

    while True:
        print("\n" + "="*50)
        print("Выберите метод:")
        print("1 - явная конечно-разностная схема")
        print("2 - неявная конечно-разностная схема") 
        print("3 - исследование зависимости погрешности от сеточных параметров")
        print("0 - выход из программы")
        method = int(input("Ваш выбор: "))
        
        if method == 0:
            break
        elif method == 3:
            research_convergence(time)
            continue
            
        print("\nВыберите уровень аппроксимации начальных условий:")
        print("1 - первого порядка")
        print("2 - второго порядка")
        approx_st = int(input("Ваш выбор: "))

        print("\nВыберите уровень аппроксимации краевых условий:")
        print("1 - двухточечная аппроксимация с первым порядком")
        print("2 - трехточечная аппроксимация со вторым порядком")
        print("3 - двухточечная аппроксимация со вторым порядком")
        approx_bo = int(input("Ваш выбор: "))

        # Вычисление решения
        if method == 1:
            # Проверка условия устойчивости для явной схемы
            stability = tau / h**2
            if stability <= 1:
                print(f"Условие Куранта выполнено: {stability:.4f} <= 1")
                U = explicit(K, 0, tau, h, x, approx_st, approx_bo)
            else:
                print(f"Условие Куранта не выполнено: {stability:.4f} > 1")
                print("Решение может быть неустойчивым!")
                continue
        elif method == 2:
            U = implicit(K, 0, tau, h, x, approx_st, approx_bo)

        # Визуализация результатов
        dt = int(input(f"\nВведите момент времени (индекс от 0 до {K-1}): "))
        
        if dt >= K:
            print("Ошибка: указанный момент времени превышает диапазон!")
            continue
            
        # Точное решение в выбранный момент времени
        U_analytic = analyt_func(x, T[dt])
        
        # Погрешность
        error = np.abs(U_analytic - U[dt, :])
        
        # График решений
        plt.figure(figsize=(15, 5))
        
        plt.subplot(1, 3, 1)
        plt.title(f"Решение в момент t = {T[dt]:.3f}")
        plt.plot(x, U_analytic, label="Точное решение", color="red", linewidth=2)
        plt.plot(x, U[dt, :], 'o-', label="Численное решение", markersize=3)
        plt.xlabel("x")
        plt.ylabel("u(x,t)")
        plt.grid(True)
        plt.legend()
        
        # График ошибки
        plt.subplot(1, 3, 2)
        plt.title("Распределение ошибки по пространству")
        plt.plot(x, error, 'g-', label="Абсолютная ошибка")
        plt.xlabel("x")
        plt.ylabel("Ошибка")
        plt.grid(True)
        plt.legend()
        
        # График ошибки во времени
        plt.subplot(1, 3, 3)
        error_time = np.zeros(len(T))
        for i in range(min(len(T), K)):
            error_time[i] = np.max(np.abs(analyt_func(x, T[i]) - U[i, :]))
        
        plt.plot(T[:len(error_time)], error_time, 'b-', label="Максимальная ошибка")
        plt.axvline(x=T[dt], color='r', linestyle='--', label=f'Выбранный момент t={T[dt]:.3f}')
        plt.xlabel("Время t")
        plt.ylabel("Максимальная ошибка")
        plt.title("Зависимость ошибки от времени")
        plt.grid(True)
        plt.legend()
        
        plt.tight_layout()
        plt.show()
        
        # Вывод информации об ошибке
        max_error = np.max(error)
        mean_error = np.mean(error)
        print(f"\nСтатистика ошибки в момент t={T[dt]:.3f}:")
        print(f"Максимальная ошибка: {max_error:.6f}")
        print(f"Средняя ошибка: {mean_error:.6f}")

    return 0

# Параметры расчета
N = 50      # Количество узлов по пространству
K = 1000    # Количество шагов по времени  
time = 2.0  # Общее время моделирования

# Запуск программы
if __name__ == "__main__":
    main(N, K, time)