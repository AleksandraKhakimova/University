import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d

def analyt_func(x, y):
    return np.exp(-y) * np.cos(x) * np.cos(y)

def func_border1(x, y):  # u(0, y) = exp(-y) * cos(y)
    return np.exp(-y) * np.cos(y)

def func_border2(x, y):  # u(π/2, y) = 0
    return 0

def func_border3(x, y):  # u(x, 0) = cos(x)
    return np.cos(x)

def func_border4(x, y):  # u(x, π/2) = 0
    return 0

def norm(cur_u, prev_u):
    max_diff = 0
    for i in range(cur_u.shape[0]):
        for j in range(cur_u.shape[1]):
            if abs(cur_u[i, j] - prev_u[i, j]) > max_diff:
                max_diff = abs(cur_u[i, j] - prev_u[i, j])
    return max_diff

def liebman(x, y, hx, hy, eps):
    Nx = len(x)
    Ny = len(y)
    count = 0
    prev_u = np.zeros((Nx, Ny))
    cur_u = np.zeros((Nx, Ny))
    
    # Инициализация граничных условий
    for i in range(Nx):
        cur_u[i, 0] = func_border3(x[i], y[0])
        cur_u[i, -1] = func_border4(x[i], y[-1])
    
    for j in range(Ny):
        cur_u[0, j] = func_border1(x[0], y[j])
        cur_u[-1, j] = func_border2(x[-1], y[j])
    
    # Коэффициенты для разностной схемы
    alpha = 1 / (hx**2)
    beta = 1 / (hy**2)
    gamma = 2 * alpha + 2 * beta + 3  # +3 из-за члена -3u
    
    while norm(cur_u, prev_u) > eps:
        count += 1
        prev_u = np.copy(cur_u)
        for i in range(1, Nx - 1):
            for j in range(1, Ny - 1):
                # Уравнение: u_xx + u_yy = -2u_y - 3u
                right_side = (alpha * (prev_u[i+1, j] + prev_u[i-1, j]) +
                             beta * (prev_u[i, j+1] + prev_u[i, j-1]) -
                             (1/hy) * (prev_u[i, j+1] - prev_u[i, j-1]))
                
                cur_u[i, j] = right_side / gamma
    
    return cur_u, count

def calculate_optimal_tau(Nx, Ny):
    """Вычисление оптимального параметра релаксации"""
    N = min(Nx, Ny)
    rho = np.cos(np.pi / N)  # спектральный радиус
    optimal_tau = 2 / (1 + np.sqrt(1 - rho**2))
    return optimal_tau

def find_best_tau(x, y, hx, hy, eps):
    """Автоматический поиск лучшего параметра"""
    print(" Поиск оптимального параметра ...")
    
    # Тестируем разные значения tau
    tau_values = [1.0, 1.2, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9]
    results = []
    
    for tau in tau_values:
        try:
            U, count = Zeidel(x, y, hx, hy, eps, tau)
            if count > 0:  # Проверяем, что метод сошелся
                results.append((tau, count))
                print(f"  tau = {tau:.1f} → {count} итераций")
        except:
            continue
    
    if not results:
        print("❌ Не удалось найти рабочий параметр")
        return 1.5  # значение по умолчанию
    
    # Находим tau с минимальным количеством итераций
    best_tau, best_count = min(results, key=lambda x: x[1])
    print(f"✅ Оптимальный параметр: tau = {best_tau:.1f} ({best_count} итераций)")
    
    return best_tau

def relaxation(x, y, hx, hy, eps, tau):
    Nx = len(x)
    Ny = len(y)
    count = 0
    prev_u = np.zeros((Nx, Ny))
    cur_u = np.zeros((Nx, Ny))
    
    # Инициализация граничных условий
    for i in range(Nx):
        cur_u[i, 0] = func_border3(x[i], y[0])
        cur_u[i, -1] = func_border4(x[i], y[-1])
    
    for j in range(Ny):
        cur_u[0, j] = func_border1(x[0], y[j])
        cur_u[-1, j] = func_border2(x[-1], y[j])
    
    # Коэффициенты для разностной схемы
    alpha = 1 / (hx**2)
    beta = 1 / (hy**2)
    gamma = 2 * alpha + 2 * beta + 3
    
    while norm(cur_u, prev_u) > eps:
        count += 1
        prev_u = np.copy(cur_u)
        for i in range(1, Nx - 1):
            for j in range(1, Ny - 1):
                right_side = (alpha * (prev_u[i+1, j] + prev_u[i-1, j]) +
                             beta * (prev_u[i, j+1] + prev_u[i, j-1]) -
                             (1/hy) * (prev_u[i, j+1] - prev_u[i, j-1]))
                
                cur_u[i, j] = (1 - tau) * prev_u[i, j] + tau * (right_side / gamma)
    
    return cur_u, count

def Zeidel(x, y, hx, hy, eps, tau):
    Nx = len(x)
    Ny = len(y)
    count = 0
    prev_u = np.zeros((Nx, Ny))
    cur_u = np.zeros((Nx, Ny))
    
    # Инициализация граничных условий
    for i in range(Nx):
        cur_u[i, 0] = func_border3(x[i], y[0])
        cur_u[i, -1] = func_border4(x[i], y[-1])
    
    for j in range(Ny):
        cur_u[0, j] = func_border1(x[0], y[j])
        cur_u[-1, j] = func_border2(x[-1], y[j])
    
    # Коэффициенты для разностной схемы
    alpha = 1 / (hx**2)
    beta = 1 / (hy**2)
    gamma = 2 * alpha + 2 * beta + 3
    
    MAX_ITERATIONS = 10000
    
    while norm(cur_u, prev_u) > eps and count < MAX_ITERATIONS:
        count += 1
        prev_u = np.copy(cur_u)
        
        for i in range(1, Nx - 1):
            for j in range(1, Ny - 1):
                # Используем уже обновленные значения
                right_side = (alpha * (prev_u[i+1, j] + cur_u[i-1, j]) +
                             beta * (prev_u[i, j+1] + cur_u[i, j-1]) -
                             (1/hy) * (prev_u[i, j+1] - cur_u[i, j-1]))
                
                cur_u[i, j] = (1 - tau) * prev_u[i, j] + tau * (right_side / gamma)
    
    return cur_u, count

def calculate_error(U_numeric, U_analytic, x, y):
    """Вычисление погрешности решения"""
    absolute_error = np.abs(U_numeric - U_analytic)
    max_error = np.max(absolute_error)
    rms_error = np.sqrt(np.mean(absolute_error**2))
    
    return absolute_error, max_error, rms_error

def main(Nx, Ny, eps):
    hx = (np.pi / 2 - 0) / (Nx - 1)
    hy = (np.pi / 2 - 0) / (Ny - 1)
    x = np.linspace(0, np.pi/2, Nx)
    y = np.linspace(0, np.pi/2, Ny)
    
    X, Y = np.meshgrid(x, y, indexing='ij')
    U_analytic = analyt_func(X, Y)
    
    # Предварительный расчет оптимального tau
    theoretical_tau = calculate_optimal_tau(Nx, Ny)
    
    while True:
        print("\nВыберите метод:")
        print("1 - метод Либмана")
        print("2 - метод Зейделя") 
        print("3 - метод простых итераций с верхней релаксацией")
        print("4 - исследование зависимости погрешности от шагов сетки")
        print("0 - выход из программы")
        
        method = int(input("Ваш выбор: "))
        
        if method == 0:
            break
            
        if method in [1, 2, 3]:
            if method == 1:
                U, count = liebman(x, y, hx, hy, eps)
                method_name = "Метод Либмана"
            elif method == 2:
                print(f"\nТеоретически оптимальный tau = {theoretical_tau:.3f}")
                choice = input("Выберите вариант:\n1 - Автоматический подбор\n2 - Ручной ввод\nВаш выбор: ")
                
                if choice == "1":
                    # Автоматический поиск лучшего tau
                    best_tau = find_best_tau(x, y, hx, hy, eps)
                    tau = best_tau
                else:
                    # Ручной ввод
                    tau = float(input("Введите параметр tau от 1 до 2: "))
                
                U, count = Zeidel(x, y, hx, hy, eps, tau)
                method_name = f"Метод Зейделя (τ={tau:.2f})"
                
            elif method == 3: 
                print(f"\nТеоретически оптимальный tau = {theoretical_tau:.3f}")
                tau = float(input("Введите параметр tau от 1 до 2: "))
                U, count = relaxation(x, y, hx, hy, eps, tau)
                method_name = f"Метод релаксации (τ={tau:.2f})"
            
            # Вычисление погрешности
            absolute_error, max_error, rms_error = calculate_error(U, U_analytic, x, y)
            
            print(f"\n{method_name}:")
            print(f"Количество итераций: {count}")
            print(f"Максимальная погрешность: {max_error:.6f}")
            print(f"Среднеквадратичная погрешность: {rms_error:.6f}")
            
            # Графики
            fig = plt.figure(figsize=(15, 5))
            
            # Точное решение
            ax1 = fig.add_subplot(131, projection='3d')
            ax1.plot_surface(X, Y, U_analytic, cmap='viridis', alpha=0.7)
            ax1.set_title('Точное решение')
            ax1.set_xlabel('x')
            ax1.set_ylabel('y')
            ax1.set_zlabel('U(x,y)')
            
            # Численное решение
            ax2 = fig.add_subplot(132, projection='3d')
            ax2.plot_surface(X, Y, U, cmap='viridis', alpha=0.7)
            ax2.set_title('Численное решение')
            ax2.set_xlabel('x')
            ax2.set_ylabel('y')
            ax2.set_zlabel('U(x,y)')
            
            # Погрешность
            ax3 = fig.add_subplot(133, projection='3d')
            error_surf = ax3.plot_surface(X, Y, absolute_error, cmap='hot', alpha=0.7)
            ax3.set_title('Абсолютная погрешность')
            ax3.set_xlabel('x')
            ax3.set_ylabel('y')
            ax3.set_zlabel('Погрешность')
            fig.colorbar(error_surf, ax=ax3, shrink=0.5)
            
            plt.suptitle(f'{method_name}, итераций: {count}, max ошибка: {max_error:.2e}')
            plt.tight_layout()
            plt.show()
            
        elif method == 4:
            # Исследование зависимости погрешности от шагов сетки
            grid_sizes = [10, 20, 30, 40, 50]
            max_errors = []
            rms_errors = []
            
            print("\nИсследование зависимости погрешности от размера сетки...")
            for N in grid_sizes:
                hx_temp = (np.pi / 2 - 0) / (N - 1)
                hy_temp = (np.pi / 2 - 0) / (N - 1)
                x_temp = np.linspace(0, np.pi/2, N)
                y_temp = np.linspace(0, np.pi/2, N)
                
                X_temp, Y_temp = np.meshgrid(x_temp, y_temp, indexing='ij')
                U_analytic_temp = analyt_func(X_temp, Y_temp)
                U_temp, _ = liebman(x_temp, y_temp, hx_temp, hy_temp, eps)
                
                _, max_err, rms_err = calculate_error(U_temp, U_analytic_temp, x_temp, y_temp)
                max_errors.append(max_err)
                rms_errors.append(rms_err)
                print(f"N={N}: max error={max_err:.6f}, RMS error={rms_err:.6f}")
            
            # График зависимости погрешности от размера сетки
            plt.figure(figsize=(10, 6))
            plt.plot(grid_sizes, max_errors, 'o-', label='Максимальная погрешность')
            plt.plot(grid_sizes, rms_errors, 's-', label='Среднеквадратичная погрешность')
            plt.xlabel('Размер сетки N')
            plt.ylabel('Погрешность')
            plt.title('Зависимость погрешности от размера сетки')
            plt.legend()
            plt.grid(True)
            plt.yscale('log')
            plt.show()

    return 0

# Параметры по умолчанию
eps = 0.0001
Nx = 30
Ny = 30

if __name__ == "__main__":
    main(Nx, Ny, eps)