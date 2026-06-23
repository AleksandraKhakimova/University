import numpy as np
import matplotlib.pyplot as plt

def sigmoid_activation(x, slope):
    """Активация сигмоидой с параметром наклона"""
    return 1.0 / (1.0 + np.exp(-slope * x))

def compute_gradient_sigmoid(output, slope):
    """Вычисление градиента для сигмоидной функции"""
    return slope * output * (1.0 - output)

class NeuralNetworkXOR:
    def __init__(self, learning_rate=0.5, slope_param=1.0):
        # Данные для задачи XOR
        self.input_patterns = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
        self.expected_outputs = np.array([[0.0], [1.0], [1.0], [0.0]])
        
        # Параметры сети
        self.learning_rate = learning_rate
        self.slope = slope_param
        
        # Инициализация весов
        self.hidden_weights = None
        self.output_weights = None
        self.init_network_params()
    
    def init_network_params(self):
        """Инициализация параметров сети"""
        # 2 входных нейрона + bias, 2 скрытых нейрона
        self.hidden_weights = np.random.uniform(-0.7, 0.7, (2, 3))
        # 2 скрытых нейрона + bias, 1 выходной нейрон
        self.output_weights = np.random.uniform(-0.7, 0.7, (1, 3))
    
    def forward_propagation(self, input_vec):
        """Прямое распространение сигнала"""
        # Добавляем bias к входному вектору
        input_with_bias = np.append(input_vec, 1.0)
        
        # Вычисление выхода скрытого слоя
        hidden_net = self.hidden_weights @ input_with_bias
        hidden_output = sigmoid_activation(hidden_net, self.slope)
        
        # Добавляем bias к выходу скрытого слоя
        hidden_with_bias = np.append(hidden_output, 1.0)
        
        # Вычисление выхода сети
        output_net = self.output_weights @ hidden_with_bias
        final_output = sigmoid_activation(output_net, self.slope)
        
        return input_with_bias, hidden_output, hidden_with_bias, final_output
    
    def backward_propagation(self, input_with_bias, hidden_output, hidden_with_bias, 
                           final_output, target):
        """Обратное распространение ошибки"""
        # Ошибка на выходе
        output_error = target - final_output
        
        # Градиент для выходного слоя
        output_grad = compute_gradient_sigmoid(final_output, self.slope)
        output_delta = output_error * output_grad
        
        # Градиент для скрытого слоя
        hidden_grad = compute_gradient_sigmoid(hidden_output, self.slope)
        hidden_delta = (output_delta * self.output_weights[:, :2].flatten()) * hidden_grad
        
        # Обновление весов
        self.output_weights += self.learning_rate * output_delta * hidden_with_bias
        self.hidden_weights += self.learning_rate * np.outer(hidden_delta, input_with_bias)
        
        # Возвращаем квадрат ошибки как скаляр
        return float(output_error**2)
    
    def train_network(self, max_iterations=1000, target_mse=0.05):
        """Обучение сети"""
        error_history = []
        
        for iteration in range(max_iterations):
            total_error = 0.0
            
            # Перемешиваем порядок представления паттернов
            indices = np.random.permutation(4)
            
            for idx in indices:
                inp = self.input_patterns[idx]
                target = self.expected_outputs[idx]
                
                # Прямое распространение
                input_bias, hidden_out, hidden_bias, network_out = self.forward_propagation(inp)
                
                # Обратное распространение и обновление весов
                pattern_error = self.backward_propagation(input_bias, hidden_out, 
                                                        hidden_bias, network_out, target)
                total_error += pattern_error
            
            # Средняя ошибка на эпоху
            avg_error = total_error / 4.0
            error_history.append(avg_error)
            
            # Проверка критерия остановки
            if avg_error <= target_mse:
                break
        
        return error_history
    
    def evaluate_performance(self):
        """Оценка работы обученной сети"""
        predictions = []
        network_outputs = []
        
        for inp in self.input_patterns:
            _, _, _, network_out = self.forward_propagation(inp)
            network_outputs.append(float(network_out[0]))  # Преобразуем в float
            predictions.append(1 if network_out[0] > 0.5 else 0)
        
        # Вычисление точности
        correct_count = 0
        for i in range(4):
            if predictions[i] == int(self.expected_outputs[i][0]):
                correct_count += 1
        
        accuracy = correct_count / 4.0 * 100.0
        
        return network_outputs, predictions, accuracy

def visualize_results(network, error_history, lr, slope):
    """Визуализация результатов обучения"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # График 1: Границы принятия решений
    ax1.set_xlim(-0.2, 1.2)
    ax1.set_ylim(-0.2, 1.2)
    ax1.set_xlabel('Вход X₁')
    ax1.set_ylabel('Вход X₂')
    ax1.set_title(f'Разделяющие границы (η={lr}, β={slope})')
    
    # Отображение разделяющих линий
    for i in range(2):
        w1, w2, bias = network.hidden_weights[i]
        if abs(w2) > 1e-6:
            x_line = np.array([-0.2, 1.2])
            y_line = -(w1 * x_line + bias) / w2
            ax1.plot(x_line, y_line, linewidth=2, 
                    label=f'Нейрон {i+1}: {w1:.2f}x₁ + {w2:.2f}x₂ + {bias:.2f}=0')
    
    # Отображение точек данных
    colors = ['red', 'blue', 'blue', 'red']
    markers = ['o', 's', 's', 'o']
    
    outputs, _, _ = network.evaluate_performance()
    for i in range(4):
        x, y = network.input_patterns[i]
        ax1.scatter(x, y, c=colors[i], s=120, marker=markers[i], 
                   edgecolors='black', linewidth=2)
        ax1.text(x + 0.05, y + 0.05, f'→{outputs[i]:.2f}', 
                fontsize=11, fontweight='bold')
    
    ax1.legend(loc='upper left', bbox_to_anchor=(1.05, 1))
    ax1.grid(True, alpha=0.3, linestyle='--')
    
    # График 2: Кривая обучения
    ax2.plot(range(1, len(error_history) + 1), error_history, 
            'b-', linewidth=2, marker='o', markersize=6)
    ax2.set_xlabel('Номер эпохи')
    ax2.set_ylabel('Среднеквадратичная ошибка')
    ax2.set_title('Динамика ошибки в процессе обучения')
    ax2.axhline(y=0.05, color='r', linestyle='--', 
               label='Целевой уровень (0.05)')
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.legend()
    ax2.set_xticks(np.arange(0, len(error_history) + 1, max(1, len(error_history)//10)))
    
    plt.tight_layout()
    plt.show()

def optimize_network_params():
    """Поиск оптимальных параметров сети"""
    param_configs = [
        {'lr': 0.8, 'slope': 0.7},
        {'lr': 0.5, 'slope': 1.0},
        {'lr': 0.3, 'slope': 1.5},
        {'lr': 0.2, 'slope': 2.0},
        {'lr': 0.1, 'slope': 3.0},
    ]
    
    best_network = None
    best_lr = 0.5
    best_slope = 1.0
    best_error_history = []
    best_final_error = float('inf')
    
    for config in param_configs:
        print(f"\nТестирование конфигурации: η={config['lr']}, β={config['slope']}")
        
        network = NeuralNetworkXOR(learning_rate=config['lr'], slope_param=config['slope'])
        error_log = network.train_network(max_iterations=500, target_mse=0.05)
        
        outputs, predictions, accuracy = network.evaluate_performance()
        final_error = error_log[-1] if error_log else 1.0
        
        print(f"  Финальная MSE: {final_error:.4f}")
        print(f"  Точность: {accuracy:.1f}%")
        
        if final_error <= 0.05:
            print(f"  ✓ Успешная конфигурация найдена!")
            return network, config['lr'], config['slope'], error_log
        
        # Сохраняем лучшую конфигурацию
        if final_error < best_final_error:
            best_final_error = final_error
            best_network = network
            best_lr = config['lr']
            best_slope = config['slope']
            best_error_history = error_log
    
    # Если не найдено подходящих параметров, используем лучшие из тестовых
    print(f"\nИспользуем лучшую найденную конфигурацию (MSE: {best_final_error:.4f})...")
    
    return best_network, best_lr, best_slope, best_error_history

def main():
    """Основная функция программы"""
    print("=" * 60)
    print("НЕЙРОННАЯ СЕТЬ ДЛЯ РЕШЕНИЯ ЗАДАЧИ XOR")
    print("=" * 60)
    
    # Поиск оптимальных параметров
    print("\nПоиск оптимальных параметров сети...")
    trained_network, optimal_lr, optimal_slope, mse_history = optimize_network_params()
    
    # Оценка работы сети
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ ОБУЧЕНИЯ")
    print("=" * 60)
    
    final_mse = mse_history[-1] if mse_history else 1.0
    outputs, predictions, accuracy = trained_network.evaluate_performance()
    
    print(f"\nОптимальные параметры:")
    print(f"  • Коэффициент обучения (η): {optimal_lr}")
    print(f"  • Параметр наклона сигмоиды (β): {optimal_slope}")
    print(f"  • Архитектура: 2 входных → 2 скрытых → 1 выходной нейрон")
    print(f"  • Финальная MSE: {final_mse:.4f}")
    
    print(f"\nКлассификация паттернов:")
    for i in range(4):
        inp = trained_network.input_patterns[i]
        expected = int(trained_network.expected_outputs[i][0])
        predicted = predictions[i]
        output_val = outputs[i]
        status = "✓" if predicted == expected else "✗"
        
        print(f"  Вход [{inp[0]}, {inp[1]}] → {output_val:.3f} → Класс {predicted} "
              f"(ожидалось: {expected}) {status}")
    
    print(f"\nТочность классификации: {accuracy:.1f}%")
    
    print("\n" + "=" * 60)
    print("ПАРАМЕТРЫ ОБУЧЕННОЙ СЕТИ")
    print("=" * 60)
    
    print("\nВеса скрытого слоя:")
    for i, weights in enumerate(trained_network.hidden_weights):
        print(f"  Нейрон {i+1}: w₁={weights[0]:.3f}, w₂={weights[1]:.3f}, смещение={weights[2]:.3f}")
    
    print("\nВеса выходного слоя:")
    output_weights = trained_network.output_weights[0]
    print(f"  w₁={output_weights[0]:.3f}, w₂={output_weights[1]:.3f}, смещение={output_weights[2]:.3f}")
    
    # Визуализация
    print("\n" + "=" * 60)
    print("ВИЗУАЛИЗАЦИЯ РЕЗУЛЬТАТОВ")
    print("=" * 60)
    
    visualize_results(trained_network, mse_history, optimal_lr, optimal_slope)
    
    print("\nОбучение завершено успешно!")

if __name__ == "__main__":
    main()