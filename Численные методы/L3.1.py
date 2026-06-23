import numpy as np
import matplotlib.pyplot as plt
from math import factorial


def f(x):
    """Исходная функция f(x) = tan(x) + x"""
    return np.tan(x) + x


def f_derivative(n, x):
    """Вычисление n-й производной функции f(x) = tan(x) + x."""
    if n == 0:
        return f(x)
    elif n == 1:
        return 1 / (np.cos(x)) ** 2 + 1
    elif n == 2:
        return 2 * np.sin(x) / (np.cos(x)) ** 3
    elif n == 3:
        return (2 + 4 * (np.sin(x)) ** 2) / (np.cos(x)) ** 4
    elif n == 4:
        return (8 * np.sin(x) + 8 * (np.sin(x)) ** 3) / (np.cos(x)) ** 5
    else:
        raise NotImplementedError("Производные выше 4-го порядка не реализованы")


def divided_diff(x, y):
    """Вычисление разделенных разностей для интерполяционного многочлена Ньютона"""
    n = len(y)
    coef = np.zeros([n, n])
    coef[:, 0] = y

    for j in range(1, n):
        for i in range(n - j):
            coef[i][j] = (coef[i + 1][j - 1] - coef[i][j - 1]) / (x[i + j] - x[i])

    return coef


def newton_poly(coef, x_data, x):
    """Вычисление значения интерполяционного многочлена Ньютона в точке x"""
    n = len(x_data) - 1
    p = coef[n]
    for k in range(1, n + 1):
        p = coef[n - k] + (x - x_data[n - k]) * p
    return p


def lagrange_poly(x, y, x_val):
    """Вычисление значения интерполяционного многочлена Лагранжа в точке x_val"""
    n = len(x)
    total = 0.0
    for i in range(n):
        li = 1.0
        for j in range(n):
            if i != j:
                li *= (x_val - x[j]) / (x[i] - x[j])
        total += li * y[i]
    return total


def omega(x_nodes, x):
    """Вычисление множителя ω_{n+1}(x) = (x-x0)(x-x1)...(x-xn)"""
    result = 1.0
    for xi in x_nodes:
        result *= (x - xi)
    return result


def estimate_error(f_derivative, x_nodes, x):
    """Оценка погрешности интерполяции по формуле (3.9)"""
    n = len(x_nodes) - 1
    # Находим максимум (n+1)-й производной на отрезке [x0, xn]
    xi = np.linspace(min(x_nodes), max(x_nodes), 1000)
    try:
        M = max(abs(f_derivative(n + 1, xi)))
    except NotImplementedError:  #Если производная нужного порядка не реализована, функция возвращает None
        print(f"Не удалось вычислить оценку погрешности: производная {n + 1}-го порядка не реализована")
        return None

    omega_val = omega(x_nodes, x)
    error_bound = (M / factorial(n + 1)) * abs(omega_val)
    return error_bound


# Вариант 14 данные
x1 = np.array([0, np.pi / 8, 2 * np.pi / 8, 3 * np.pi / 8])  # первый набор узлов
x2 = np.array([0, np.pi / 8, np.pi / 3, 3 * np.pi / 8])  # второй набор узлов
x_star = 3 * np.pi / 16  # точка для вычисления

# Вычисляем значения функции в узлах
y1 = f(x1)
y2 = f(x2)

# Интерполяция Лагранжа
L1 = lagrange_poly(x1, y1, x_star)
L2 = lagrange_poly(x2, y2, x_star)

# Интерполяция Ньютона
# Вычисляем разделенные разницы
dd1 = divided_diff(x1, y1)
dd2 = divided_diff(x2, y2)

# Берем первые элементы каждой строки (верхнюю диагональ)
coef_newton1 = dd1[0, :]
coef_newton2 = dd2[0, :]

# Вычисляем полином Ньютона
N1 = newton_poly(coef_newton1, x1, x_star)
N2 = newton_poly(coef_newton2, x2, x_star)

# Точное значение в точке x_star
y_star = f(x_star)

# Погрешности
error_L1 = abs(L1 - y_star)
error_L2 = abs(L2 - y_star)
error_N1 = abs(N1 - y_star)
error_N2 = abs(N2 - y_star)

# Оценки погрешностей по формуле (3.9)
error_bound1 = estimate_error(f_derivative, x1, x_star)
error_bound2 = estimate_error(f_derivative, x2, x_star)

print("Результаты для первого набора узлов:")
print(f"Метод Лагранжа: L(x*) = {L1:.6f}, точное значение = {y_star:.6f}, погрешность = {error_L1:.6f}")
print(f"Метод Ньютона: N(x*) = {N1:.6f}, точное значение = {y_star:.6f}, погрешность = {error_N1:.6f}")
if error_bound1 is not None:
    print(f"Теоретическая оценка погрешности: {error_bound1:.6f}\n")

print("Результаты для второго набора узлов:")
print(f"Метод Лагранжа: L(x*) = {L2:.6f}, точное значение = {y_star:.6f}, погрешность = {error_L2:.6f}")
print(f"Метод Ньютона: N(x*) = {N2:.6f}, точное значение = {y_star:.6f}, погрешность = {error_N2:.6f}")
if error_bound2 is not None:
    print(f"Теоретическая оценка погрешности: {error_bound2:.6f}")

# Визуализация
x_plot = np.linspace(0, 3 * np.pi / 8, 100)
y_plot = f(x_plot)

plt.figure(figsize=(12, 6))
plt.plot(x_plot, y_plot, label='f(x) = tan(x) + x')
plt.scatter(x1, y1, color='red', label='Узлы интерполяции 1')
plt.scatter(x2, y2, color='green', label='Узлы интерполяции 2')
plt.scatter([x_star], [y_star], color='black', label=f'x* = {x_star:.3f}')
plt.legend()
plt.grid()
plt.title('Интерполяция функции f(x) = tan(x) + x')
plt.xlabel('x')
plt.ylabel('f(x)')
plt.show()