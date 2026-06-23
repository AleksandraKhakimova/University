import numpy as np
import matplotlib.pyplot as plt

def plot_function_f(x):
    return x**3 - 2*x**2 - 10*x + 15

def function_fi(x):
    return (2*x**2 + 10*x - 15)**(1/3)

def function_f(x):
    return x**3 - 2*x**2 - 10*x + 15

def derivative_f(x):
    return 3*x**2 - 4*x - 10

def simple_iter(e, q, a, b):
    roots0 = a
    roots1 = function_fi((a + b) / 2)
    while q / (1 - q) * abs(roots0 - roots1) > e:
        roots0 = roots1
        roots1 = function_fi(roots1)
    return roots1

def newton_method(e, a, b):
    roots0 = (a + b) / 2  # Начальное приближение - середина отрезка
    roots1 = roots0 - function_f(roots0) / derivative_f(roots0)
    while abs(roots0 - roots1) > e:
        roots0 = roots1
        roots1 = roots0 - function_f(roots0) / derivative_f(roots0)
    return roots1

def main():
    e = 0.0001
    q = 0.2
    plt.title("График функции x³ - 2x² - 10x + 15")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.grid()
    plt.axis([-5, 5, -20, 20])  # Изменены границы для лучшего отображения
    x = np.arange(-5, 5, 0.1)
    y = plot_function_f(x)
    plt.plot(x, y)
    plt.axhline(0, color='black', linewidth=0.5)
    plt.show()

    print("Введите границы отрезка, на котором производится поиск корня:")
    a, b = map(float, input().split(' '))

    print("Методом простых итераций:\n"
          "Корнем уравнения на промежутке от", a, "до", b, "является", np.around(simple_iter(e, q, a, b), 5))
    print("Методом Ньютона:\n"
          "Корнем уравнения на промежутке от", a, "до", b, "является", np.around(newton_method(e, a, b), 5))

main()