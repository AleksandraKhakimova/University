
#Модуль для создания тестовых сигналов с помехами.
#Содержит функцию create_test_signal, которая ВОЗВРАЩАЕТ данные.


import numpy as np


def create_test_signal(T=2.0, fs=10000, seed=42):
    
   # Создает тестовый сигнал: полезный сигнал + высокочастотные помехи + шум.
  
    t = np.linspace(0, T, int(fs * T))
    
    # Полезный сигнал: 2 Гц
    f_signal = 2.0
    u = np.sin(2 * np.pi * f_signal * t)
    
    # Высокочастотные помехи
    f_noise1, f_noise2, f_noise3 = 45.0, 120.0, 250.0
    A1, A2, A3 = 0.2, 0.15, 0.1
    
    v_sin = (A1 * np.sin(2 * np.pi * f_noise1 * t) + 
             A2 * np.sin(2 * np.pi * f_noise2 * t) + 
             A3 * np.sin(2 * np.pi * f_noise3 * t))
    
    # Белый шум
    noise_power = 0.1
    np.random.seed(seed)
    v_noise = noise_power * np.random.randn(len(t))
    
    # Импульсная помеха
    v_impulse = np.zeros_like(t)
    impulse_time = int(1.0 * fs)
    impulse_width = int(0.01 * fs)
    v_impulse[impulse_time:impulse_time+impulse_width] = 1.0
    
    # Суммируем помехи
    v = v_sin + v_noise + v_impulse
    g = u + v
    
    params = {
        'T': T, 'fs': fs, 'f_signal': f_signal,
        'f_noise': [f_noise1, f_noise2, f_noise3],
        'A_noise': [A1, A2, A3], 'noise_power': noise_power,
        'seed': seed, 'snr_db': 20 * np.log10(1.0 / np.std(v))
    }
    
    return {
        't': t, 'u': u, 'v_sin': v_sin, 'v_noise': v_noise,
        'v_impulse': v_impulse, 'v': v, 'g': g, 'params': params
    }


def analyze_spectrum(t, signal):
   
  #  Анализирует спектр сигнала через БПФ.
    
   
    dt = t[1] - t[0]
    n = len(signal)
    
    fft_vals = np.fft.fft(signal)
    fft_freqs = np.fft.fftfreq(n, dt)
    
    positive = fft_freqs > 0
    freqs = fft_freqs[positive]
    spectrum = np.abs(fft_vals[positive]) * 2.0 / n
    
    return freqs, spectrum


if __name__ == "__main__":
    # Демонстрация тестового сигнала
    import matplotlib.pyplot as plt
    
    data = create_test_signal(T=2.0, fs=10000, seed=42)
    
    t = data['t']
    u = data['u']
    g = data['g']
    params = data['params']
    
    plt.figure(figsize=(14, 8))
    
    plt.subplot(2, 1, 1)
    n_show = 3000
    plt.plot(t[:n_show], u[:n_show], 'b-', linewidth=1.5, label='Полезный')
    plt.plot(t[:n_show], g[:n_show], 'purple', alpha=0.7, linewidth=1, label='Зашумленный')
    plt.xlabel('Время (с)')
    plt.ylabel('Амплитуда')
    plt.title(f'Тестовый сигнал (SNR = {params["snr_db"]:.1f} дБ)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xlim([0, 0.3])
    
    plt.subplot(2, 1, 2)
    freqs, spec_g = analyze_spectrum(t, g)
    freqs, spec_u = analyze_spectrum(t, u)
    
    freq_limit = 300
    mask = freqs < freq_limit
    
    plt.semilogy(freqs[mask], spec_g[mask], 'purple', label='Зашумленный')
    plt.semilogy(freqs[mask], spec_u[mask], 'b--', label='Полезный')
    plt.axvline(5, color='black', linestyle='--', label='f_среза')
    plt.xlabel('Частота (Гц)')
    plt.ylabel('Амплитуда')
    plt.title('Спектры сигналов')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xlim([0, freq_limit])
    
    plt.tight_layout()
    plt.show()