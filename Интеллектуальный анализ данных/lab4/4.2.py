import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_recall_curve, precision_score, recall_score, f1_score, roc_auc_score, roc_curve
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import RobustScaler
import matplotlib.pyplot as plt
import seaborn as sns

# Загрузка данных
data = pd.read_excel('/Users/sasahakimova/Downloads/4/Titanic.xlsx')
print("=" * 70)
print("АНАЛИЗ ВЫЖИВАЕМОСТИ НА ТИТАНИКЕ С ИСПОЛЬЗОВАНИЕМ НЕЙРОННЫХ СЕТЕЙ")
print("=" * 70)
print(f"Исходный размер данных: {data.shape}")
print(f"Первые 5 записей:")
print(data.head())
print("\n" + "-" * 70)

# Улучшенная предобработка данных
def preprocess_data(df):
    df_clean = df.copy()
    
    # Удаление ненужных столбцов
    df_clean = df_clean.drop(['PassengerId', 'Ticket', 'Cabin'], axis=1, errors='ignore')
    
    # Извлечение новых признаков из имени
    df_clean['Title'] = df_clean['Name'].str.extract(' ([A-Za-z]+)\.', expand=False)
    df_clean['Title'] = df_clean['Title'].replace(['Lady', 'Countess','Capt', 'Col', 'Don', 'Dr', 
                                                  'Major', 'Rev', 'Sir', 'Jonkheer', 'Dona'], 'Rare')
    df_clean['Title'] = df_clean['Title'].replace('Mlle', 'Miss')
    df_clean['Title'] = df_clean['Title'].replace('Ms', 'Miss')
    df_clean['Title'] = df_clean['Title'].replace('Mme', 'Mrs')
    
    # Создание семейных признаков
    df_clean['FamilySize'] = df_clean['SibSp'] + df_clean['Parch'] + 1
    df_clean['IsAlone'] = 0
    df_clean.loc[df_clean['FamilySize'] == 1, 'IsAlone'] = 1

    df_clean['Age'] = pd.to_numeric(df_clean['Age'], errors='coerce')
    title_age_median = df_clean.groupby('Title')['Age'].transform('median')
    df_clean['Age'] = df_clean['Age'].fillna(title_age_median)
    df_clean['Age'] = df_clean['Age'].fillna(df_clean['Age'].median())
    
    # Создание возрастных групп
    df_clean['AgeGroup'] = pd.cut(df_clean['Age'], bins=[0, 12, 18, 35, 60, 100], 
                                 labels=['Child', 'Teen', 'Adult', 'Middle', 'Senior'])
    
    # Обработка Fare с созданием групп
    df_clean['Fare'] = pd.to_numeric(df_clean['Fare'], errors='coerce')
    df_clean['Fare'] = df_clean['Fare'].fillna(df_clean['Fare'].median())
    df_clean['FareGroup'] = pd.qcut(df_clean['Fare'], 4, labels=[1, 2, 3, 4])
    
    # Заполнение пропущенных значений в Embarked
    df_clean['Embarked'] = df_clean['Embarked'].fillna(df_clean['Embarked'].mode()[0])

    df_clean = df_clean.drop(['Name'], axis=1, errors='ignore')
    
    # Кодирование категориальных переменных
    le_sex = LabelEncoder()
    le_embarked = LabelEncoder()
    le_title = LabelEncoder()
    le_agegroup = LabelEncoder()
    le_faregroup = LabelEncoder()
    
    df_clean['Sex'] = le_sex.fit_transform(df_clean['Sex'])
    df_clean['Embarked'] = le_embarked.fit_transform(df_clean['Embarked'])
    df_clean['Title'] = le_title.fit_transform(df_clean['Title'])
    df_clean['AgeGroup'] = le_agegroup.fit_transform(df_clean['AgeGroup'])
    df_clean['FareGroup'] = le_faregroup.fit_transform(df_clean['FareGroup'])
    
    # Статистика по данным
    print("ИНФОРМАЦИЯ О ДАННЫХ ПОСЛЕ ПРЕДОБРАБОТКИ:")
    print(f"Количество признаков: {df_clean.shape[1]}")
    print(f"Количество записей: {df_clean.shape[0]}")
    print(f"Пропущенные значения: {df_clean.isnull().sum().sum()}")
    print(f"Распределение целевой переменной (Survived):")
    print(df_clean['Survived'].value_counts())
    print(f"Доля выживших: {df_clean['Survived'].mean():.2%}")
    print("-" * 70)
    
    return df_clean, le_sex, le_embarked, le_title, le_agegroup, le_faregroup

data_cleaned, le_sex, le_embarked, le_title, le_agegroup, le_faregroup = preprocess_data(data)

# Разделение на признаки и целевую переменную
X = data_cleaned.drop('Survived', axis=1)
y = data_cleaned['Survived']

# Стратифицированное разделение с фиксированным random_state для воспроизводимости
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Использую RobustScaler вместо StandardScaler, так как он менее чувствителен выбросам
scaler = RobustScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"Размер тренировочной выборки: {X_train_scaled.shape}")
print(f"Размер тестовой выборки: {X_test_scaled.shape}")
print(f"Количество признаков: {X_train_scaled.shape[1]}")

# Улучшенная функция поиска порога с визуализацией
def find_balanced_threshold(model, X_val, y_val, min_precision=0.65, min_recall=0.65):
    y_proba = model.predict_proba(X_val)[:, 1]
    precision, recall, thresholds = precision_recall_curve(y_val, y_proba)
    
    best_threshold = 0.5
    best_f1 = 0
    thresholds_metrics = []
    
    # Ищем порог с хорошим балансом precision и recall
    for i, thresh in enumerate(thresholds):
        y_pred_temp = (y_proba > thresh).astype(int)
        temp_recall = recall_score(y_val, y_pred_temp)
        temp_precision = precision_score(y_val, y_pred_temp)
        
        # Рассчитываем F1-score
        if temp_precision + temp_recall > 0:
            temp_f1 = 2 * (temp_precision * temp_recall) / (temp_precision + temp_recall)
        else:
            temp_f1 = 0
        
        thresholds_metrics.append((thresh, temp_precision, temp_recall, temp_f1))
        
        # Условия: precision И recall выше минимальных
        if temp_precision >= min_precision and temp_recall >= min_recall:
            if temp_f1 > best_f1:
                best_f1 = temp_f1
                best_threshold = thresh

    # Если не нашли подходящий порог, используем порог с максимальным F1
    if best_threshold == 0.5 and len(thresholds_metrics) > 0:
        thresholds_metrics.sort(key=lambda x: x[3], reverse=True)
        best_threshold = thresholds_metrics[0][0]
        best_f1 = thresholds_metrics[0][3]
    
    print(f"\nОПТИМАЛЬНЫЙ ПОРОГ КЛАССИФИКАЦИИ:")
    print(f"Выбранный порог: {best_threshold:.3f}")
    print(f"Соответствующий F1-score: {best_f1:.3f}")
    
    return best_threshold

# Улучшенная архитектура нейросети
print("\n" + "=" * 70)
print("НАСТРОЙКА МОДЕЛИ НЕЙРОННОЙ СЕТИ")
print("=" * 70)

mlp_improved = MLPClassifier(
    hidden_layer_sizes=(100, 50),  # 2 скрытых слоя
    activation='relu',
    solver='adam',
    alpha=0.001,  # Нормальная регуляризация
    batch_size=32,
    learning_rate='constant',
    learning_rate_init=0.001,
    max_iter=500,
    random_state=42,
    early_stopping=True,
    validation_fraction=0.2,
    n_iter_no_change=20,
    tol=1e-4,
    verbose=False
)

# Создание валидационной выборки
X_train_sub, X_val, y_train_sub, y_val = train_test_split(
    X_train_scaled, y_train, test_size=0.2, random_state=42, stratify=y_train
)

print("ОБУЧЕНИЕ МОДЕЛИ...")
mlp_improved.fit(X_train_sub, y_train_sub)

print("ПОДБОР ОПТИМАЛЬНОГО ПОРОГА КЛАССИФИКАЦИИ...")
balanced_threshold = find_balanced_threshold(mlp_improved, X_val, y_val, min_precision=0.65, min_recall=0.65)

print("\nПЕРЕОБУЧЕНИЕ НА ВСЕЙ ТРЕНИРОВОЧНОЙ ВЫБОРКЕ...")
mlp_improved.fit(X_train_scaled, y_train)

# Прогнозирование
y_proba_test = mlp_improved.predict_proba(X_test_scaled)[:, 1]
y_pred_balanced = (y_proba_test > balanced_threshold).astype(int)

# Расчет метрик
y_train_pred = mlp_improved.predict(X_train_scaled)
train_accuracy = accuracy_score(y_train, y_train_pred)
test_accuracy = accuracy_score(y_test, y_pred_balanced)
test_recall = recall_score(y_test, y_pred_balanced)
test_precision = precision_score(y_test, y_pred_balanced)
test_f1 = f1_score(y_test, y_pred_balanced)
test_roc_auc = roc_auc_score(y_test, y_proba_test)

# Итоги
print("\n" + "=" * 70)
print("РЕЗУЛЬТАТЫ ОБУЧЕНИЯ МОДЕЛИ")
print("=" * 70)

print("\n📊 ТЕХНИЧЕСКИЕ ПАРАМЕТРЫ МОДЕЛИ:")
print(f"• Архитектура сети: {mlp_improved.hidden_layer_sizes}")
print(f"• Функция активации: {mlp_improved.activation}")
print(f"• Оптимизатор: {mlp_improved.solver}")
print(f"• Скорость обучения: {mlp_improved.learning_rate_init}")
print(f"• Количество итераций обучения: {mlp_improved.n_iter_}")
print(f"• Финальное значение функции потерь: {mlp_improved.loss_:.4f}")

print("\n🧮 АРХИТЕКТУРА НЕЙРОННОЙ СЕТИ:")
print(f"Всего слоев (включая входной и выходной): {len(mlp_improved.coefs_) + 1}")
print(f"Входной слой: {X_train_scaled.shape[1]} признаков")
for i, (coef, intercept) in enumerate(zip(mlp_improved.coefs_, mlp_improved.intercepts_)):
    if i == len(mlp_improved.coefs_) - 1:
        print(f"→ Выходной слой: {coef.shape[0]} нейронов -> {coef.shape[1]} выход (Survived)")
    else:
        print(f"→ Скрытый слой {i+1}: {coef.shape[0]} входов -> {coef.shape[1]} нейронов")

print("\n" + "=" * 70)
print("📈 ОЦЕНКА КАЧЕСТВА МОДЕЛИ")
print("=" * 70)

print(f"\n✅ ТРЕНИРОВОЧНАЯ ВЫБОРКА:")
print(f"   Точность (Accuracy): {train_accuracy:.4f}")

print(f"\n🧪 ТЕСТОВАЯ ВЫБОРКА:")
print(f"   Точность (Accuracy): {test_accuracy:.4f}")
print(f"   Precision (точность предсказания выживших): {test_precision:.4f}")
print(f"   Recall (полнота выявления выживших): {test_recall:.4f}")
print(f"   F1-Score (баланс Precision и Recall): {test_f1:.4f}")
print(f"   ROC-AUC Score: {test_roc_auc:.4f}")
print(f"   Используемый порог классификации: {balanced_threshold:.3f}")

print("\n📊 МАТРИЦА ОШИБОК (Confusion Matrix):")
cm = confusion_matrix(y_test, y_pred_balanced)
cm_df = pd.DataFrame(cm, 
                     index=['Фактически погиб (0)', 'Фактически выжил (1)'],
                     columns=['Предсказано погиб (0)', 'Предсказано выжил (1)'])
print(cm_df)

print("\n📄 ДЕТАЛЬНЫЙ ОТЧЕТ КЛАССИФИКАЦИИ:")
print(classification_report(y_test, y_pred_balanced, target_names=['Погиб', 'Выжил']))

# Дополнительная статистика
tn, fp, fn, tp = cm.ravel()
print("\n📈 ДОПОЛНИТЕЛЬНАЯ СТАТИСТИКА:")
print(f"• True Negative (Правильно предсказаны погибшие): {tn}")
print(f"• False Positive (Ошибочно предсказаны выжившие): {fp}")
print(f"• False Negative (Ошибочно предсказаны погибшие): {fn}")
print(f"• True Positive (Правильно предсказаны выжившие): {tp}")
print(f"• Специфичность (Specificity): {tn/(tn+fp):.3f}" if (tn+fp) > 0 else "• Специфичность: N/A")
print(f"• Точность предсказания погибших: {tn/(tn+fn):.3f}" if (tn+fn) > 0 else "• Точность предсказания погибших: N/A")

print("\n" + "=" * 70)
print("🎯 ИНТЕРПРЕТАЦИЯ РЕЗУЛЬТАТОВ:")
print("=" * 70)

if test_accuracy > 0.8:
    print("✓ Отличное качество модели!")
elif test_accuracy > 0.75:
    print("✓ Хорошее качество модели")
elif test_accuracy > 0.7:
    print("✓ Удовлетворительное качество модели")
else:
    print("⚠ Модель требует дополнительной настройки")

if test_recall > test_precision:
    print("• Модель лучше выявляет выживших (высокий Recall)")
elif test_precision > test_recall:
    print("• Модель точнее в предсказании выживших (высокий Precision)")
else:
    print("• Сбалансированное качество по Precision и Recall")

print(f"\n💡 РЕКОМЕНДАЦИИ:")
print(f"1. Текущий порог классификации: {balanced_threshold:.3f}")
print("2. Для увеличения Recall (выявления большего числа выживших) - уменьшите порог")
print("3. Для увеличения Precision (точности предсказания выживших) - увеличьте порог")
print("4. ROC-AUC {:.3f} указывает на {} способность модели различать классы".format(
    test_roc_auc, 
    "отличную" if test_roc_auc > 0.9 else "хорошую" if test_roc_auc > 0.8 else "удовлетворительную" if test_roc_auc > 0.7 else "низкую"
))

print("\n" + "=" * 70)
print("🏁 АНАЛИЗ ЗАВЕРШЕН")
print("=" * 70)
