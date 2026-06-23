import numpy as np

#Задание 5: реализуем алгоритм QR для нахождения собственных значений и собственных векторов матриц
print("\nЗадание № 5\n")
#определяем знак числа, вдальнейщем для корректного выполнения вычислений с векторами
def sign(x):
    if x > 0:
        return 1
    if x < 0:
        return -1
    else:
        return 0
#Создаем транспонированную матрицы
def transpose(A):
    AT = np.zeros((A.shape[0], A.shape[1]))  #Инициализация матрицы AT с той же размерностью, что и A
    for i in range(A.shape[0]):
        for j in range(A.shape[1]):
            AT[j,i] = A[i,j]  #Транспонирование: строки становятся столбцами
    return AT

#Умножаем две матрицы A и B с помощью стандартного алгоритма умножения
def multiply(A,B):
    C = np.zeros((A.shape[0], A.shape[1]))  # Инициализация результирующей матрицы C
    for i in range(C.shape[0]):
        for j in range(C.shape[1]):
            for k in range(C.shape[1]):  # По всем элементам строки A и столбца B
                C[i,j] += A[i,k] * B[k,j]  # Умножение матриц
    return C

#Поэлементное деление матрицы А на число B
def division(A,B):
    C = np.zeros((A.shape[0], A.shape[1]))  # Инициализация результирующей матрицы C
    for i in range(C.shape[0]):
        for j in range(C.shape[1]):
            C[i,j] = A[i,j] / B  # Делим каждый элемент матрицы A на B
    return C

#Поэлементное вычитание матрицы В из матрицы А
def difference(A,B):
    C = np.zeros((A.shape[0], A.shape[1]))
    for i in range(C.shape[0]):
        for j in range(C.shape[1]):
            C[i,j] = A[i,j] - B[i,j]  # Вычитаем элементы матрицы B из матрицы A
    return C

#Вычисляем норму вектора
def norm_vector(b):
    norm = 0  # Инициализация переменной для хранения нормы вектора
    for i in range(len(b)):  # Проход по всем элементам вектора
        norm += b[i]*b[i]  # Суммируем квадрат каждого элемента
    return np.sqrt(norm)  # Возвращаем норму вектора

#Создаем матрицу Хаусхолдера, которая используется для превращения (рефакторирования) матрицы
# в верхнюю треугольную форму, что является частью QR-алгоритма.
def Householder_matrix(H, index):
    H1 = np.copy(H)  # Копия матрицы H
    x1 = np.zeros(H1.shape[1])  # Инициализация вектора x1
    b = np.zeros(H1.shape[1])  # Инициализация вектора b
    for k in range(H1.shape[1]):  # Проход по столбцам матрицы
        b[k] = H1[k,index]  # Заполнение вектора b элементами столбца с заданным индексом
    norm = norm_vector(b)  # Вычисление нормы вектора b
    for i in range(H1.shape[0]):  # Проход по строкам матрицы
        if i == index:
            x1[i] = H1[i,index] + sign(H1[i,index]) * norm  # Корректировка элемента (вычисление x1)
        elif i < index:
            x1[i] = 0  # Установка нуля для элементов выше заданного индекса
        else:
            x1[i] = H1[i,index]  # Оставляем элементы ниже индекса без изменений
    v1 = np.zeros((len(x1),len(x1)))  # Инициализация вектора v1
    for i in range(v1.shape[1]):
        v1[i,0] = x1[i]  # Заполнение вектора v1
    v1_T = transpose(v1)  # Транспонирование вектора v1
    E = np.eye(H1.shape[0])  # Создание единичной матрицы размером H1
    H1 = difference(E, 2*(division(multiply(v1,v1_T), multiply(v1_T,v1)[0,0])))  # Формирование матрицы Хаусхолдера
    return H1  # Возвращает матрицу Хаусхолдера H1

#Выполняем разложение матрицы A на произведение матрицы Q (производной от матриц Хаусхолдера)
# и верхней треугольной матрицы R
def QR(A):
    A0 = np.copy(A)  # Копируем исходную матрицу A
    H = []  # Список для хранения матриц Хаусхолдера
    for i in range(A.shape[0] - 1):  # Для каждого столбца матрицы
        H0 = Householder_matrix(A0, i)  # Получаем матрицу Хаусхолдера
        A0 = multiply(H0, A0)  # Умножаем текущую матрицу на матрицу Хаусхолдера
        H.append(H0)  # Добавляем матрицу Хаусхолдера в список
    for i in range(len(H) - 1):  # Применяем произведение матриц Хаусхолдера
        H[i + 1] = multiply(H[i], H[i + 1])  # Перемножаем последовательно
    return A0, H[-1]  # Возвращаем верхнюю треугольную матрицу и последнюю матрицу Хаусхолдера

#Вычисляем собственные значения матрицы A
# с использованием QR-алгоритма до тех пор, пока матрица не достигнет заданной точности
def eigenvalues(A, max_iter=1000, tol=1e-6, epsilon=1e-6):
    # Создаем копию входной матрицы, чтобы не изменять оригинал
    A0 = np.copy(A)
    # Получаем размерность квадратной матрицы (n x n)
    n = A0.shape[0]
    # Основной цикл QR-алгоритма (максимальное число итераций - max_iter)
    for _ in range(max_iter):
        # Выполняем QR-разложение текущей матрицы A0
        R, Q = QR(A0)
        # Обновляем матрицу A0: A0 = R * Q (следующая итерация алгоритма)
        A0 = multiply(R, Q)
        # Проверка сходимости: вычисляем нижний треугольник (без диагонали)
        lower_tri = np.tril(A0, k=-1)
        # Если максимальный элемент в нижнем треугольнике меньше tol - выходим
        if np.max(np.abs(lower_tri)) < tol:
            break
    # Инициализация списка для хранения собственных значений
    L = []
    i = 0
    while i < n:
        if i < n - 1 and np.abs(A0[i + 1, i]) > tol:
            # Обработка блока 2x2
            a, b, c, d = A0[i, i], A0[i, i + 1], A0[i + 1, i], A0[i + 1, i + 1]
            trace = a + d
            det = a * d - b * c
            discriminant = trace ** 2 - 4 * det

            if discriminant < 0:
                # Комплексно-сопряженные корни
                real_part = (a22 + a33) / 2
                imag_part = np.sqrt(-discriminant) / 2
                lambda2 = complex(real_part, imag_part)
                lambda3 = complex(real_part, -imag_part)

                # Округляем до двух знаков после запятой, как в примере
                lambda1 = round(lambda1, 2)
                lambda2 = complex(round(lambda2.real, 2), round(lambda2.imag, 2))
                lambda3 = complex(round(lambda3.real, 2), round(lambda3.imag, 2))

                return [lambda1, lambda2, lambda3]

            elif discriminant > 0:
                # Два различных действительных корня
                sqrt_discr = np.sqrt(discriminant)
                lambda2 = (a22 + a33 + sqrt_discr) / 2
                lambda3 = (a22 + a33 - sqrt_discr) / 2

                # Округляем до двух знаков после запятой
                lambda1 = round(lambda1, 2)
                lambda2 = round(lambda2, 2)
                lambda3 = round(lambda3, 2)

                return [lambda1, lambda2, lambda3]
            else:
                # Кратный действительный корень
                lambda2 = (a22 + a33) / 2
                lambda3 = lambda2

                # Округляем до двух знаков после запятой
                lambda1 = round(lambda1, 2)
                lambda2 = round(lambda2, 2)
                lambda3 = round(lambda3, 2)

                return [lambda1, lambda2, lambda3]

        # Если не выполнились специальные условия, возвращаем диагональные элементы
        return [round(A0[i, i], 2) for i in range(n)]шлд

#Проверка
def check_eigenvalues(A, eigenvalues, epsilon):
    n = A.shape[0]
    for λ in eigenvalues:
        if isinstance(λ, complex):
            # Для комплексных чисел проверяем действительную и мнимую части
            v = np.random.rand(n) + 1j * np.random.rand(n)
        else:
            v = np.random.rand(n)

        Av = multiply(A, v.reshape(-1, 1)).flatten()
        λv = λ * v
        error = np.max(np.abs(Av - λv))

        if error > epsilon:
            return False
    return True



#Выполняем QR-разложение и вычисляем собственные значения для заданной матрицы
def main(A):
    Q = QR(A)[1]  # Получаем матрицу Q из QR-разложения
    R = QR(A)[0]  # Получаем матрицу R из QR-разложения
    print("Матрица Q:\n", QR(A)[1])
    print("Матрица R:\n", QR(A)[0])
    print("Собственные значения матрицы А:\n", eigenvalues(A))


A = np.array([[2.0, -4.0, 5.0],
             [-5.0, -2.0, -3.0],
             [1.0, -8.0, -3.0]])
main(A)
