import numpy as np
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt

# Данные из варианта 14
x = np.array([0.0, 0.9, 1.8, 2.7, 3.6])
y = np.array([0.0, 0.72235, 1.5609, 2.8459, 7.7275])
X_star = 1.5  # Точка для вычисления значения


def natural_cubic_spline(x, y, X):
    """Построение естественного кубического сплайна и вычисление его значения в точке X."""
    n = len(x) - 1  # Количество интервалов

    # 1. Проверка, что X находится в пределах интервала [x[0], x[-1]]
    if X < x[0] or X > x[-1]:
        raise ValueError(f"Точка X={X} находится вне интервала [{x[0]}, {x[-1]}]")

    # 2. Вычисление h_i - разницы между x_i+1 и x_i
    h = np.diff(x)

    # 3. Построение системы уравнений для нахождения вторых производных (M)
    # Создаем матрицу системы и вектор правой части
    A = np.zeros((n + 1, n + 1))     # Матрица (n+1) x (n+1), заполненная нулями
    b = np.zeros(n + 1)            # Вектор длины (n+1), заполненный нулями

    # Естественный сплайн: M_0 = M_n = 0 (нулевая кривизна на концах)
    A[0, 0] = 1
    A[n, n] = 1

    # Проверка выполнения условия нулевой кривизны на концах
    print("Проверка условий нулевой кривизны на концах:")
    print(f"M[0] = 0: {A[0, 0] == 1 and b[0] == 0}")
    print(f"M[n] = 0: {A[n, n] == 1 and b[n] == 0}")

    # Заполняем матрицу для внутренних точек
    for i in range(1, n):
        A[i, i - 1] = h[i - 1]        # Коэффициент при M_{i-1}
        A[i, i] = 2 * (h[i - 1] + h[i])      # Коэффициент при M_i
        A[i, i + 1] = h[i]          # Коэффициент при M_{i+1}
        b[i] = 3 * ((y[i + 1] - y[i]) / h[i] - (y[i] - y[i - 1]) / h[i - 1])

    # 4. Решаем систему для нахождения M
    M = np.linalg.solve(A, b)

    # 5. Находим коэффициенты сплайна для каждого интервала
    coeffs = []
    for i in range(n):
        a = y[i]
        b = (y[i + 1] - y[i]) / h[i] - h[i] * (2 * M[i] + M[i + 1]) / 3
        c = M[i]
        d = (M[i + 1] - M[i]) / (3 * h[i])
        coeffs.append([a, b, c, d])

    # 6. Находим, в каком интервале находится X
    interval = np.searchsorted(x, X) - 1
    interval = max(0, min(interval, n - 1))  # Ограничиваем диапазон

    # Проверка, что X находится в правильном интервале
    if not (x[interval] <= X <= x[interval + 1]):
        raise ValueError(f"Точка X={X} не находится в интервале [{x[interval]}, {x[interval + 1]}]")

    # 7. Вычисляем значение сплайна в точке X
    dx = X - x[interval]
    spline_value = coeffs[interval][0] + coeffs[interval][1] * dx + coeffs[interval][2] * dx ** 2 + coeffs[interval][
        3] * dx ** 3

    return spline_value, coeffs


# Вычисление значения в точке X*
try:
    spline_value, coeffs = natural_cubic_spline(x, y, X_star)
    true_value = np.interp(X_star, x, y)  # Линейная интерполяция для сравнения

    print(f"\nЗначение кубического сплайна в точке X* = {X_star}: {spline_value:.6f}")
    print(f"Линейная интерполяция в точке X*: {true_value:.6f}")
    print("\nКоэффициенты сплайна для каждого интервала:")
    for i, c in enumerate(coeffs):
        print(f"Интервал [{x[i]:.1f}, {x[i + 1]:.1f}]: a={c[0]:.6f}, b={c[1]:.6f}, c={c[2]:.6f}, d={c[3]:.6f}")
except ValueError as e:
    print(f"Ошибка: {e}")

# Визуализация
x_plot = np.linspace(x[0], x[-1], 100)
y_spline = []
for xi in x_plot:
    try:
        y_spline.append(natural_cubic_spline(x, y, xi)[0])
    except ValueError:
        y_spline.append(np.nan)

plt.figure(figsize=(10, 6))
plt.plot(x, y, 'o', label='Узлы интерполяции')
plt.plot(x_plot, y_spline, label='Кубический сплайн')
plt.axvline(X_star, color='r', linestyle='--', label=f'X* = {X_star}')
plt.legend()
plt.grid()
plt.title('Кубический сплайн с нулевой кривизной на границах')
plt.xlabel('x')
plt.ylabel('f(x)')
plt.show()