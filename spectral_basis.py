"""
Модуль для работы с ортогональными базисами на отрезке [0, T].
Поддерживаются базисы: тригонометрический (косинусоиды), полиномы Лежандра, функции Хаара.
"""

import numpy as np
from scipy.integrate import quad
import matplotlib.pyplot as plt


class SpectralBasis:
    """
    Класс для работы с ортогональными базисами на отрезке [0, T].
    Обеспечивает вычисление спектральных коэффициентов сигнала,
    восстановление сигнала по коэффициентам и матрицу дифференцирования.
    """
    
    def __init__(self, L, T=2.0, basis_type='trigonometric'):
        """
        Инициализация спектрального базиса.
        
        Параметры:
        L : int - количество базисных функций (рекомендуется степень двойки для базиса Хаара)
        T : float - длина интервала [0, T]
        basis_type : str - тип базиса ('trigonometric', 'legendre', 'haar')
        """
        self.L = L
        self.T = T
        self.basis_type = basis_type
        
        # Создаем ортонормированный базис
        self.basis_functions = self._create_basis()
        
        # Вычисляем матрицу дифференцирования P
        self.P = self._compute_P_matrix()
        
        print(f"Инициализирован базис: {basis_type}, L = {L}, T = {T}")
        print(f"Размер матрицы дифференцирования P: {self.P.shape}")
        print(f"Норма матрицы P: {np.linalg.norm(self.P, 2):.4f}")
    
    def _create_basis(self):
        """Создает ортонормированный базис на интервале [0, T]."""
        if self.basis_type == 'trigonometric':
            return self._create_trigonometric_basis()
        elif self.basis_type == 'legendre':
            return self._create_legendre_basis()
        elif self.basis_type == 'haar':
            return self._create_haar_basis()
        else:
            raise ValueError(f"Неизвестный тип базиса: {self.basis_type}")
    
    def _create_trigonometric_basis(self):
        """
        Ортонормированные косинусоиды.
        φ_0(t) = 1/√T
        φ_i(t) = √(2/T) cos(i·π·t/T), i = 1, 2, ...
        """
        basis = []
        
        # Постоянная составляющая
        def const_func(t):
            return 1.0 / np.sqrt(self.T)
        basis.append(const_func)
        
        # Косинусоиды
        for i in range(1, self.L):
            def cos_func(t, n=i):
                return np.sqrt(2.0 / self.T) * np.cos(n * np.pi * t / self.T)
            basis.append(cos_func)
        
        return basis[:self.L]
    
    def _create_legendre_basis(self):
        """
        Ортонормированные полиномы Лежандра на отрезке [0, T].
        Используется аффинное преобразование τ = 2t/T - 1 ∈ [-1, 1].
        φ_i(t) = √((2i+1)/T) · P_i(τ)
        """
        basis = []
        
        # Аффинное преобразование
        def tau(t):
            return 2 * t / self.T - 1
        
        # Рекуррентное вычисление полиномов Лежандра
        def legendre_poly(n, t):
            tau_val = tau(t)
            if n == 0:
                return np.ones_like(t)
            elif n == 1:
                return tau_val
            else:
                P_prev2 = np.ones_like(t)
                P_prev1 = tau_val
                for k in range(1, n):
                    P_curr = ((2*k + 1) * tau_val * P_prev1 - k * P_prev2) / (k + 1)
                    P_prev2, P_prev1 = P_prev1, P_curr
                return P_prev1
        
        for i in range(self.L):
            def legendre_func(t, n=i):
                return np.sqrt((2*n + 1) / self.T) * legendre_poly(n, t)
            basis.append(legendre_func)
        
        return basis
    
    def _create_haar_basis(self):
       
        basis = []
        
        # Порождающая вейвлет-функция Хаара
        def haar_wavelet(tau):
            result = np.zeros_like(tau)
            mask1 = (tau >= 0) & (tau < 0.5)
            mask2 = (tau >= 0.5) & (tau < 1)
            result[mask1] = 1
            result[mask2] = -1
            return result
        
        # Постоянная составляющая
        def const_func(t):
            return 1.0 / np.sqrt(self.T)
        basis.append(const_func)
        
        # Функции Хаара
        idx = 1
        m = 0
        while idx < self.L:
            for k in range(2**m):
                if idx >= self.L:
                    break
                def haar_func(t, mm=m, kk=k):
                    tau = 2**mm * t / self.T - kk
                    return np.sqrt(2**mm / self.T) * haar_wavelet(tau)
                basis.append(haar_func)
                idx += 1
            m += 1
        
        return basis[:self.L]
    
    def _compute_P_matrix(self):
        """Вычисляет матрицу дифференцирования P по аналитическим формулам."""
        if self.basis_type == 'trigonometric':
            return self._compute_P_trigonometric()
        elif self.basis_type == 'legendre':
            return self._compute_P_legendre()
        elif self.basis_type == 'haar':
            return self._compute_P_haar()
        else:
            raise ValueError(f"Неизвестный тип базиса: {self.basis_type}")
    
    def _compute_P_trigonometric(self):
        """
        Матрица дифференцирования для базиса косинусоид.
        Элементы: P_ij = ∫ φ_i(t) φ'_j(t) dt + φ_i(0)φ_j(0)
        """
        P = np.zeros((self.L, self.L))
        
        for i in range(self.L):
            for j in range(self.L):
                if i == 0 and j == 0:
                    P[i, j] = 1.0
                elif i == 0 and j > 0:
                    P[i, j] = (-1)**j * np.sqrt(2)
                elif i > 0 and j == 0:
                    P[i, j] = np.sqrt(2)
                elif i == j and i > 0:
                    P[i, j] = 2.0
                elif i > 0 and j > 0 and i != j:
                    P[i, j] = 2 * (i**2 - (-1)**(i+j) * j**2) / (i**2 - j**2)
        
        # Масштабирование по времени
        P = P / self.T
        return P
    
    def _compute_P_legendre(self):
        """
        Матрица дифференцирования для базиса полиномов Лежандра.
        """
        P = np.zeros((self.L, self.L))
        
        for i in range(self.L):
            for j in range(self.L):
                if i < j:
                    P[i, j] = np.sqrt((2*j + 1) * (2*i + 1))
                elif i > j:
                    P[i, j] = (-1)**(i - j) * np.sqrt((2*j + 1) * (2*i + 1))
                else:  # i == j
                    P[i, j] = 2*i + 1
        
        # Масштабирование по времени
        P = P / self.T
        return P
    
    def _compute_P_haar(self):
        """
        Матрица дифференцирования для базиса Хаара.
        Вычисляется численно с помощью интегрирования.
        """
        P = np.zeros((self.L, self.L))
        
        # P[0,0] = 1
        P[0, 0] = 1.0
        
        # Для остальных элементов используем численное интегрирование
        for i in range(self.L):
            for j in range(self.L):
                if i == 0 and j == 0:
                    continue
                # Интеграл ∫ φ_i(t) φ'_j(t) dt
                def integrand(t):
                    return self.basis_functions[i](t) * self._derivative_of_basis(j, t)
                P[i, j], _ = quad(integrand, 0, self.T, limit=200, epsabs=1e-10)
        
        # Добавляем граничные члены φ_i(0)φ_j(0)
        for i in range(self.L):
            for j in range(self.L):
                P[i, j] += self.basis_functions[i](0) * self.basis_functions[j](0)
        
        return P
    
    def _derivative_of_basis(self, j, t):
        """Вычисляет производную j-й базисной функции (численно)."""
        dt = 1e-6
        t_plus = t + dt
        t_minus = t - dt
        return (self.basis_functions[j](t_plus) - self.basis_functions[j](t_minus)) / (2 * dt)
    
    def compute_spectrum(self, signal_func):
        """
        Вычисляет спектральные коэффициенты G для заданной функции.
        
        Параметры:
        signal_func : callable - функция сигнала f(t)
        
        Возвращает:
        G : numpy array - вектор спектральных коэффициентов
        """
        G = np.zeros(self.L)
        
        for i in range(self.L):
            integrand = lambda t: signal_func(t) * self.basis_functions[i](t)
            G[i], _ = quad(integrand, 0, self.T, limit=200, epsabs=1e-8)
        
        return G
    
    def reconstruct_signal(self, G, t_points):
        """
        Восстанавливает сигнал из спектральных коэффициентов.
        
        Параметры:
        G : numpy array - вектор спектральных коэффициентов
        t_points : numpy array - временные точки для восстановления
        
        Возвращает:
        signal : numpy array - восстановленный сигнал
        """
        signal = np.zeros_like(t_points)
        
        for i in range(self.L):
            basis_values = np.array([self.basis_functions[i](t) for t in t_points])
            signal += G[i] * basis_values
        
        return signal
    
    def get_P_matrix(self):
        """Возвращает матрицу дифференцирования P."""
        return self.P
    
    def visualize_basis(self, num_points=1000):
        #Визуализирует первые несколько базисных функций
        t = np.linspace(0, self.T, num_points)
        
        basis_names = {
            'trigonometric': 'косинусоиды',
            'legendre': 'полиномы Лежандра',
            'haar': 'функции Хаара'
        }
        basis_name_ru = basis_names.get(self.basis_type, self.basis_type)
        
        plt.figure(figsize=(12, 8))
        
        for i in range(min(6, self.L)):
            basis_values = [self.basis_functions[i](ti) for ti in t]
            plt.plot(t, basis_values, label=f'φ_{i}(t)')
        
        plt.xlabel('Время t, с')
        plt.ylabel('φᵢ(t)')
        plt.title(f'Базисные функции: {basis_name_ru}')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()


if __name__ == "__main__":
    # Демонстрация работы с различными базисами
    T = 2.0
    L = 8  # Степень двойки для корректного сравнения
    
    # Базис косинусоид
    print("\n" + "="*50)
    print("Базис косинусоид")
    print("="*50)
    basis_cos = SpectralBasis(L, T, basis_type='trigonometric')
    basis_cos.visualize_basis()
    
    # Базис полиномов Лежандра
    print("\n" + "="*50)
    print("Базис полиномов Лежандра")
    print("="*50)
    basis_leg = SpectralBasis(L, T, basis_type='legendre')
    basis_leg.visualize_basis()
    
    # Базис функций Хаара
    print("\n" + "="*50)
    print("Базис функций Хаара")
    print("="*50)
    basis_haar = SpectralBasis(L, T, basis_type='haar')
    basis_haar.visualize_basis()