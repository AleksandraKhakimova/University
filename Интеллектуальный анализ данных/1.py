import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Данные
data = {
    'X': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
    'Y': [5, 4, 7, 15, 18, 20, 23, 26, 29, 34, 37, 41, 28, 30, 49, 51, 54, 38]
}
df = pd.DataFrame(data)

# Функция для вывода полной описательной статистики
def print_descriptive_stats(column, name):
    print(f"\n{'='*60}")
    print(f"ОПИСАТЕЛЬНАЯ СТАТИСТИКА ДЛЯ {name}")
    print('='*60)
    
    # Основные показатели
    print(f"Среднее: {column.mean():.5f}")
    print(f"Медиана: {column.median():.5f}")
    
    # Мода (может быть несколько значений)
    mode_result = column.mode()
    if len(mode_result) > 0:
        print(f"Мода: {mode_result.values}")
    else:
        print("Мода: #Н/Д")
    
    print(f"Стандартное отклонение: {column.std(ddof=0):.5f}")
    print(f"Дисперсия выборки: {column.var(ddof=0):.5f}")
    print(f"Стандартная ошибка: {column.sem():.5f}")
    print(f"Асимметричность: {column.skew():.5f}")
    print(f"Эксцесс: {column.kurtosis():.5f}")
    print(f"Интервал (размах): {column.max() - column.min()}")
    print(f"Минимум: {column.min()}")
    print(f"Максимум: {column.max()}")
    print(f"Сумма: {column.sum()}")
    print(f"Счет: {len(column)}")
    print(f"Наибольший(1): {column.max()}")
    print(f"Наименьший(1): {column.min()}")
    
    # Уровень надежности (95%)
    ci = stats.t.interval(0.95, len(column)-1, loc=column.mean(), scale=column.sem())
    print(f"Уровень надежности (95.0)%: {ci[1] - column.mean():.5f}")

# 1. Описательная статистика для X
print_descriptive_stats(df['X'], 'X')

# 2. Описательная статистика для Y
print_descriptive_stats(df['Y'], 'Y')

# 3. Box plot для Y
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
sns.boxplot(y=df['Y'], color='lightblue')
plt.title('Ящик с усами для Y')
plt.ylabel('Y')

plt.tight_layout()
plt.show()

# 4. Линейная регрессия
slope, intercept, r_value, p_value, std_err = stats.linregress(df['X'], df['Y'])
print(f"\n{'='*60}")
print("ЛИНЕЙНАЯ РЕГРЕССИЯ")
print('='*60)
print(f"Уравнение: Y = {intercept:.4f} + {slope:.4f} * X")
print(f"Коэффициент корреляции (r): {r_value:.4f}")
print(f"Коэффициент детерминации (R²): {r_value**2:.4f}")
print(f"Стандартная ошибка оценки: {std_err:.4f}")
print(f"p-значение: {p_value:.4f}")

# Прогнозные значения
df['Y_pred'] = intercept + slope * df['X']

# 5. График регрессии
plt.figure(figsize=(10, 6))
plt.scatter(df['X'], df['Y'], color='blue', alpha=0.7, s=80, label='Исходные данные')
plt.plot(df['X'], df['Y_pred'], color='red', linewidth=2.5, 
         label=f'Y = {intercept:.2f} + {slope:.2f}X (R²={r_value**2:.3f})')

# Добавляем линию тренда через seaborn для сравнения
sns.regplot(x='X', y='Y', data=df, scatter=False, 
            line_kws={'color': 'green', 'linestyle': '--', 'alpha': 0.5})

plt.xlabel('X', fontsize=12)
plt.ylabel('Y', fontsize=12)
plt.title('Линейная регрессия Y от X', fontsize=14)
plt.legend(fontsize=11)
plt.grid(True, alpha=0.3)

# Добавляем аннотацию с уравнением
equation_text = f'Y = {intercept:.2f} + {slope:.2f}X\nR² = {r_value**2:.3f}'
plt.annotate(equation_text, xy=(0.05, 0.95), xycoords='axes fraction',
             fontsize=11, bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))

plt.tight_layout()
plt.show()

# 6. Дополнительная таблица с основными статистиками
print(f"\n{'='*60}")
print("СВОДНАЯ ТАБЛИЦА ОСНОВНЫХ СТАТИСТИК")
print('='*60)

summary_data = {
    'Показатель': ['Среднее', 'Медиана', 'Стандартное отклонение', 
                   'Дисперсия', 'Минимум', 'Максимум', 'Размах', 'Сумма', 'Количество'],
    'X': [df['X'].mean(), df['X'].median(), df['X'].std(ddof=0),
          df['X'].var(ddof=0), df['X'].min(), df['X'].max(),
          df['X'].max() - df['X'].min(), df['X'].sum(), len(df['X'])],
    'Y': [df['Y'].mean(), df['Y'].median(), df['Y'].std(ddof=0),
          df['Y'].var(ddof=0), df['Y'].min(), df['Y'].max(),
          df['Y'].max() - df['Y'].min(), df['Y'].sum(), len(df['Y'])]
}

summary_df = pd.DataFrame(summary_data)
print(summary_df.to_string(index=False, float_format='{:,.4f}'.format))

