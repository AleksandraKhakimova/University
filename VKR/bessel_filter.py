"""
Модуль для построения фильтра Бесселя спектральным методом.
Реализовано вычисление коэффициентов фильтра для произвольного порядка.
"""

import numpy as np
from scipy.linalg import svd, eigvals
from scipy.signal import bessel, freqs
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

from spectral_basis import SpectralBasis


class BesselFilter:
    """
    Фильтр Бесселя, построенный спектральным методом.
    Используется аппроксимация двумерной нестационарной передаточной функции
    фильтра в выбранном ортогональном базисе.
    """
    
    def __init__(self, basis: SpectralBasis, order: int = 2, cutoff_freq: float = 5.0):
        """
        Инициализация фильтра Бесселя.
        
        Параметры:
        basis : SpectralBasis - объект класса спектрального базиса
        order : int - порядок фильтра (поддерживаются произвольные порядки)
        cutoff_freq : float - частота среза в Гц
        """
        self.basis = basis
        self.order = order
        self.fc = cutoff_freq
        self.L = basis.L
        self.P = basis.get_P_matrix()
        self.omega_c = 2 * np.pi * cutoff_freq
        
        # Вычисляем коэффициенты фильтра Бесселя для заданного порядка
        self.num_const, self.denom_coeffs = self._compute_bessel_coeffs(order)
        
        # Строим матрицу W - аппроксимацию передаточной функции фильтра
        self.W = self._build_W_matrix()
        
        print(f"\n🔍 Создан фильтр Бесселя {order}-го порядка, f_c = {cutoff_freq} Гц")
        print(f"   Базис: {basis.basis_type}")
        print(f"   Размер матрицы W: {self.W.shape}")
        print(f"   Норма W: {np.linalg.norm(self.W, 2):.4f}")
    
    def _compute_bessel_coeffs(self, n):
        """
        Вычисляет коэффициенты полинома Бесселя B_n(s) = sum_{k=0}^{n} a_k s^k.
        
        Используется рекуррентное соотношение:
        B_0(s) = 1
        B_1(s) = s + 1
        B_n(s) = (2n-1) * B_{n-1}(s) + s^2 * B_{n-2}(s)
        
        Возвращает:
        num_const : float - нормировочный коэффициент (значение B_n(0))
        denom_coeffs : list - коэффициенты знаменателя от младшей степени к старшей
        """
        if n == 0:
            return 1.0, [1.0]
        if n == 1:
            return 1.0, [1.0, 1.0]
        
        # Начальные полиномы в виде списков коэффициентов [a0, a1, ..., ak]
        # B_0(s) = 1
        B_prev2 = [1.0]
        # B_1(s) = s + 1
        B_prev1 = [1.0, 1.0]
        
        for k in range(2, n + 1):
            # Вычисляем B_k = (2k-1) * B_{k-1} + s^2 * B_{k-2}
            
            # Часть 1: (2k-1) * B_{k-1}
            coeff1 = [(2*k - 1) * c for c in B_prev1]
            
            # Часть 2: s^2 * B_{k-2} (сдвиг коэффициентов на 2 степени вверх)
            coeff2 = [0.0, 0.0] + B_prev2
            
            # Суммируем полиномы
            max_len = max(len(coeff1), len(coeff2))
            coeff1_ext = coeff1 + [0.0] * (max_len - len(coeff1))
            coeff2_ext = coeff2 + [0.0] * (max_len - len(coeff2))
            
            B_curr = [coeff1_ext[i] + coeff2_ext[i] for i in range(max_len)]
            
            # Сдвигаем для следующей итерации
            B_prev2, B_prev1 = B_prev1, B_curr
        
        # B_n(0) = первый коэффициент (a0)
        num_const = B_prev1[0]
        denom_coeffs = B_prev1
        
        return num_const, denom_coeffs
    
    def _build_W_matrix(self):
        
        #Строит матрицу W фильтра Бесселя.
    
        I = np.eye(self.L)
        P_scaled = self.P / self.omega_c
        
        # Строим матричный полином A = a0*I + a1*P + a2*P^2 + ... + an*P^n
        A = self.denom_coeffs[0] * I
        
        P_power = I.copy()  # P^0
        for k in range(1, len(self.denom_coeffs)):
            P_power = P_power @ P_scaled  # P^k
            A += self.denom_coeffs[k] * P_power
        
        # Обращение матрицы через SVD для обеспечения численной устойчивости
        # SVD позволяет корректно обрабатывать плохо обусловленные матрицы
        U, s, Vt = svd(A)
        tol = 1e-8 * max(s)
        s_inv = np.zeros_like(s)
        s_inv[s > tol] = 1.0 / s[s > tol]
        A_inv = Vt.T @ np.diag(s_inv) @ U.T
        
        W = self.num_const * A_inv
        
        # Проверка устойчивости фильтра по спектральному радиусу
        eig_vals = eigvals(W)
        max_eig = np.max(np.abs(eig_vals))
        self._is_stable = max_eig < 1.0
        
        if not self._is_stable:
            print(f"   ⚠️ Внимание: спектральный радиус W = {max_eig:.4f} > 1")
        
        return W
    
    def _bessel_polynomial(self, s):
        """
        Вычисляет полином Бесселя B_n(s) для заданного s.
        Используется для аналитических расчетов АЧХ и ФЧХ.
        """
        if self.order == 0:
            return np.ones_like(s)
        elif self.order == 1:
            return s + 1
        else:
            B_prev2 = np.ones_like(s)
            B_prev1 = s + 1
            
            for n in range(2, self.order + 1):
                B_curr = (2*n - 1) * B_prev1 + s**2 * B_prev2
                B_prev2, B_prev1 = B_prev1, B_curr
            
            return B_prev1
    
    def analytic_gain(self, frequency):
        """
        Возвращает аналитический коэффициент усиления на заданной частоте.
        
        Параметры:
        frequency : float - частота в Гц
        
        Возвращает:
        H : float - модуль передаточной функции
        """
        w = 2 * np.pi * frequency
        s = 1j * w
        s_norm = s / self.omega_c
        H = np.abs(self.num_const / self._bessel_polynomial(s_norm))
        return H
    
    def analytic_group_delay(self, frequency):
   
        w = 2 * np.pi * frequency
        w_norm = w / self.omega_c
        
        # Для малых порядков используем аналитические формулы
        if self.order == 1:
            tau = 1 / (1 + w_norm**2)
        elif self.order == 2:
            w2 = w_norm**2
            numerator = 3 * (3 + w2)
            denominator = (3 - w2)**2 + 9 * w2
            tau = numerator / denominator
        elif self.order == 3:
            w2 = w_norm**2
            numerator = 15 * (15 + 6*w2 + w2**2)
            denominator = (15 - 6*w2)**2 + (15*w2 - w2**2)**2
            tau = numerator / denominator
        elif self.order == 4:
            w2 = w_norm**2
            w4 = w2**2
            numerator = 105 * (105 + 45*w2 + 6*w4)
            denominator = (105 - 45*w2 + w4)**2 + (105*w2 - 10*w2**2)**2
            tau = numerator / denominator
        else:
            # Для высоких порядков используем численное дифференцирование
            def phase_func(w_norm):
                s = 1j * w_norm
                H = self.num_const / self._bessel_polynomial(s)
                return np.angle(H)
            
            dw = 1e-6
            phi = phase_func(w_norm)
            phi_plus = phase_func(w_norm + dw)
            phi_minus = phase_func(w_norm - dw)
            dphi_dw = (phi_plus - phi_minus) / (2 * dw)
            tau = -dphi_dw
        
        tau = tau / self.omega_c
        return tau
    
    def get_group_delay_scipy(self, frequencies):
        """
        Вычисляет групповую задержку с помощью scipy.signal для верификации.
        
        Параметры:
        frequencies : array - частоты в Гц
        
        Возвращает:
        group_delay : array - групповая задержка в секундах
        """
        omega = 2 * np.pi * frequencies
        
        # Создаем аналоговый фильтр Бесселя
        b, a = bessel(self.order, self.omega_c, analog=True, norm='phase')
        
        # Частотная характеристика
        w, h = freqs(b, a, omega)
        
        # Вычисление групповой задержки
        phi = np.unwrap(np.angle(h))
        group_delay = -np.gradient(phi, omega)
        
        return group_delay
    
    def apply_filter(self, signal_func):
      
        t = np.linspace(0, self.basis.T, 2000)
        G = self.basis.compute_spectrum(signal_func)
        X = self.W @ G
        y = self.basis.reconstruct_signal(X, t)
        return t, y
    
    def get_gain(self, frequency):
        """Возвращает аналитический коэффициент усиления."""
        return self.analytic_gain(frequency)
    
    def get_group_delay(self, frequency):
        """Возвращает аналитическую групповую задержку."""
        return self.analytic_group_delay(frequency)
    
    def frequency_response(self, frequencies):
        """Вычисляет АЧХ фильтра для заданных частот."""
        H_analytic = np.array([self.analytic_gain(f) for f in frequencies])
        return H_analytic
    
    
    
