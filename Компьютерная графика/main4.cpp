
#include <GL/glew.h>
#include <GLFW/glfw3.h>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <iostream>
#include <vector>
#include <cmath>
#include <fstream>
#include <sstream>

// Функция загрузки и компиляции шейдеров
GLuint LoadShader(const char* vertexPath, const char* fragmentPath);

// Функции для отрисовки объектов
void drawCube();
void drawSphere(float radius, unsigned int sectorCount, unsigned int stackCount);
void drawPyramid(float size);

// Обработчик ввода
void processInput(GLFWwindow* window);

// Размеры окна
const unsigned int SCR_WIDTH = 800;
const unsigned int SCR_HEIGHT = 600;

// Инициализация состояния источников света
bool directionalLightOn = true;
bool pointLightOn = true;

// Основная функция
int main() {
    // Инициализация GLFW
    if (!glfwInit()) {
        std::cerr << "Failed to initialize GLFW" << std::endl;
        return -1;
    }

    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

    // Создаем окно
    GLFWwindow* window = glfwCreateWindow(SCR_WIDTH, SCR_HEIGHT, "OpenGL Scene with GLEW", nullptr, nullptr);
    if (!window) {
        std::cerr << "Failed to create GLFW window" << std::endl;
        glfwTerminate();
        return -1;
    }
    glfwMakeContextCurrent(window);

    // Инициализация GLEW
    glewExperimental = GL_TRUE;
    if (glewInit() != GLEW_OK) {
        std::cerr << "Failed to initialize GLEW" << std::endl;
        return -1;
    }

    // Компиляция шейдеров
    GLuint shaderProgram = LoadShader("vertex_shader.glsl", "fragment_shader.glsl");

    // Установка матрицы проекции
    glm::mat4 projection = glm::perspective(glm::radians(45.0f), (float)SCR_WIDTH / (float)SCR_HEIGHT, 0.1f, 100.0f);
    
    // Включаем глубокое тестирование (для корректной отрисовки)
    glEnable(GL_DEPTH_TEST);

    // Основной цикл отрисовки
    while (!glfwWindowShouldClose(window)) {
        // Обработка ввода
        processInput(window);

        // Очистка буферов
        glClearColor(0.1f, 0.1f, 0.1f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

        // Активация шейдера
        glUseProgram(shaderProgram);

        // Установка источников света
        glUniform1i(glGetUniformLocation(shaderProgram, "directionalLightOn"), directionalLightOn);
        glUniform1i(glGetUniformLocation(shaderProgram, "pointLightOn"), pointLightOn);

        // Настройка камеры
        glm::mat4 view = glm::lookAt(glm::vec3(0.0f, 0.0f, 6.0f), glm::vec3(0.0f, 0.0f, 0.0f), glm::vec3(0.0f, 1.0f, 0.0f));
        glUniformMatrix4fv(glGetUniformLocation(shaderProgram, "view"), 1, GL_FALSE, &view[0][0]);
        glUniformMatrix4fv(glGetUniformLocation(shaderProgram, "projection"), 1, GL_FALSE, &projection[0][0]);

        // Отрисовка объектов (куб, сфера и пирамида)

        // Куб
        glm::mat4 model = glm::translate(glm::mat4(1.0f), glm::vec3(-2.0f, 0.0f, 0.0f));
        glUniformMatrix4fv(glGetUniformLocation(shaderProgram, "model"), 1, GL_FALSE, &model[0][0]);
        drawCube();

        // Сфера
        model = glm::translate(glm::mat4(1.0f), glm::vec3(0.0f, 0.0f, -2.0f));
        glUniformMatrix4fv(glGetUniformLocation(shaderProgram, "model"), 1, GL_FALSE, &model[0][0]);
        drawSphere(1.0f, 36, 18);

        // Пирамида
        model = glm::translate(glm::mat4(1.0f), glm::vec3(2.0f, 0.0f, 0.0f));
        glUniformMatrix4fv(glGetUniformLocation(shaderProgram, "model"), 1, GL_FALSE, &model[0][0]);
        drawPyramid(1.0f);

        // Обновление окна
        glfwSwapBuffers(window);
        glfwPollEvents();
    }

    // Завершение работы
    glfwTerminate();
    return 0;
}

// Функция обработки ввода для включения/отключения источников света
void processInput(GLFWwindow* window) {
    if (glfwGetKey(window, GLFW_KEY_ESCAPE) == GLFW_PRESS)
        glfwSetWindowShouldClose(window, true);

    if (glfwGetKey(window, GLFW_KEY_1) == GLFW_PRESS)
        directionalLightOn = !directionalLightOn;

    if (glfwGetKey(window, GLFW_KEY_2) == GLFW_PRESS)
        pointLightOn = !pointLightOn;
}

// Функция загрузки и компиляции шейдеров
GLuint LoadShader(const char* vertexPath, const char* fragmentPath) {
    // Чтение шейдеров из файлов
    std::string vertexCode;
    std::string fragmentCode;
    std::ifstream vShaderFile;
    std::ifstream fShaderFile;

    vShaderFile.exceptions(std::ifstream::failbit | std::ifstream::badbit);
    fShaderFile.exceptions(std::ifstream::failbit | std::ifstream::badbit);
    try {
        vShaderFile.open(vertexPath);
        fShaderFile.open(fragmentPath);
        std::stringstream vShaderStream, fShaderStream;

        vShaderStream << vShaderFile.rdbuf();
        fShaderStream << fShaderFile.rdbuf();

        vShaderFile.close();
        fShaderFile.close();

        vertexCode = vShaderStream.str();
        fragmentCode = fShaderStream.str();
    } catch (std::ifstream::failure& e) {
        std::cerr << "ERROR::SHADER::FILE_NOT_SUCCESFULLY_READ" << std::endl;
        return 0;
    }

    const char* vShaderCode = vertexCode.c_str();
    const char* fShaderCode = fragmentCode.c_str();

    // Компиляция вершинного шейдера
    GLuint vertexShader = glCreateShader(GL_VERTEX_SHADER);
    glShaderSource(vertexShader, 1, &vShaderCode, nullptr);
    glCompileShader(vertexShader);

    // Проверка ошибок компиляции вершинного шейдера
    int success;
    char infoLog[512];
    glGetShaderiv(vertexShader, GL_COMPILE_STATUS, &success);
    if (!success) {
        glGetShaderInfoLog(vertexShader, 512, nullptr, infoLog);
        std::cerr << "ERROR::SHADER::VERTEX::COMPILATION_FAILED\n" << infoLog << std::endl;
        return 0;
    }

    // Компиляция фрагментного шейдера
    GLuint fragmentShader = glCreateShader(GL_FRAGMENT_SHADER);
    glShaderSource(fragmentShader, 1, &fShaderCode, nullptr);
    glCompileShader(fragmentShader);

    // Проверка ошибок компиляции фрагментного шейдера
    glGetShaderiv(fragmentShader, GL_COMPILE_STATUS, &success);
    if (!success) {
        glGetShaderInfoLog(fragmentShader, 512, nullptr, infoLog);
        std::cerr << "ERROR::SHADER::FRAGMENT::COMPILATION_FAILED\n" << infoLog << std::endl;
        return 0;
    }

    // Связывание шейдерной программы
    GLuint shaderProgram = glCreateProgram();
    glAttachShader(shaderProgram, vertexShader);
    glAttachShader(shaderProgram, fragmentShader);
    glLinkProgram(shaderProgram);

    // Проверка ошибок связывания
    glGetProgramiv(shaderProgram, GL_LINK_STATUS, &success);
    if (!success) {
        glGetProgramInfoLog(shaderProgram, 512, nullptr, infoLog);
        std::cerr << "ERROR::SHADER::PROGRAM::LINKING_FAILED\n" << infoLog << std::endl;
        return 0;
    }

    // Очистка ресурсов шейдеров
    glDeleteShader(vertexShader);
    glDeleteShader(fragmentShader);

    return shaderProgram;
}

// Функция для отрисовки куба
void drawCube() {
    float vertices[] = {
        // позиции          // цвета
        -0.5f, -0.5f, -0.5f, 1.0f, 0.0f, 0.0f,
         0.5f, -0.5f, -0.5f, 0.0f, 1.0f, 0.0f,
         0.5f,  0.5f, -0.5f, 0.0f, 0.0f, 1.0f,
         0.5f,  0.5f, -0.5f, 0.0f, 0.0f, 1.0f,
        -0.5f,  0.5f, -0.5f, 1.0f, 1.0f, 0.0f,
        -0.5f, -0.5f, -0.5f, 1.0f, 0.0f, 0.0f,

        -0.5f, -0.5f,  0.5f, 1.0f, 0.0f, 0.0f,
         0.5f, -0.5f,  0.5f, 0.0f, 1.0f, 0.0f,
         0.5f,  0.5f,  0.5f, 0.0f, 0.0f, 1.0f,
         0.5f,  0.5f,  0.5f, 0.0f, 0.0f, 1.0f,
        -0.5f,  0.5f,  0.5f, 1.0f, 1.0f, 0.0f,
        -0.5f, -0.5f,  0.5f, 1.0f, 0.0f, 0.0f,

        -0.5f,  0.5f,  0.5f, 1.0f, 1.0f, 0.0f,
        -0.5f,  0.5f, -0.5f, 1.0f, 1.0f, 0.0f,
        -0.5f, -0.5f, -0.5f, 1.0f, 0.0f, 0.0f,
        -0.5f, -0.5f,  0.5f, 0.0f, 1.0f, 0.0f,
        -0.5f,  0.5f,  0.5f, 1.0f, 1.0f, 0.0f,
        -0.5f, -0.5f, -0.5f, 1.0f, 0.0f, 0.0f,

        0.5f,  0.5f,  0.5f, 1.0f, 0.0f, 0.0f,
        0.5f,  0.5f, -0.5f, 0.0f, 1.0f, 0.0f,
        0.5f, -0.5f, -0.5f, 0.0f, 0.0f, 1.0f,
        0.5f, -0.5f,  0.5f, 0.0f, 0.0f, 1.0f,
        0.5f,  0.5f,  0.5f, 1.0f, 0.0f, 0.0f,
        0.5f, -0.5f, -0.5f, 0.0f, 1.0f, 0.0f,
    };

    unsigned int VBO, VAO;
    glGenVertexArrays(1, &VAO);
    glGenBuffers(1, &VBO);
    
    glBindVertexArray(VAO);
    
    glBindBuffer(GL_ARRAY_BUFFER, VBO);
    glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);
    
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(float), (void*)0);
    glEnableVertexAttribArray(0);
    
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(float), (void*)(3 * sizeof(float)));
    glEnableVertexAttribArray(1);
    
    glDrawArrays(GL_TRIANGLES, 0, 36);
    
    glBindVertexArray(0);
    glDeleteBuffers(1, &VBO);
    glDeleteVertexArrays(1, &VAO);
}

// Функция для отрисовки сферы
void drawSphere(float radius, unsigned int sectorCount, unsigned int stackCount) {
    std::vector<float> vertices; // Вершины для рисования
    std::vector<unsigned int> indices; // Индексы для соединения вершин

    float x, y, z, xy; 
    float sectorStep = 2 * M_PI / sectorCount; 
    float stackStep = M_PI / stackCount;
    float sectorAngle, stackAngle;

    // Генерация вершин и нормалей для сферы
    for (unsigned int i = 0; i <= stackCount; ++i) {
        stackAngle = M_PI / 2 - i * stackStep;  // от 90 до -90
        xy = radius * cosf(stackAngle);         // r * cos(phi)
        z = radius * sinf(stackAngle);          // r * sin(phi)

        for (unsigned int j = 0; j <= sectorCount; ++j) {
            sectorAngle = j * sectorStep;        // от 0 до 2PI

            x = xy * cosf(sectorAngle);  // r * cos(phi) * cos(theta)
            y = xy * sinf(sectorAngle);  // r * cos(phi) * sin(theta)

            // Добавляем вершины и нормали
            vertices.push_back(x); 
            vertices.push_back(y);
            vertices.push_back(z);
            
            // Нормали для каждой вершины
            float length = sqrt(x * x + y * y + z * z); // Нормализуем вектор
            vertices.push_back(x / length);  // Нормаль по X
            vertices.push_back(y / length);  // Нормаль по Y
            vertices.push_back(z / length);  // Нормаль по Z
        }
    }

    // Генерация индексов для отрисовки треугольниками
    for (unsigned int i = 0; i < stackCount; ++i) {
        for (unsigned int j = 0; j < sectorCount; ++j) {
            unsigned int first = (i * (sectorCount + 1)) + j;
            unsigned int second = first + sectorCount + 1;

            // Строим два треугольника для каждой ячейки
            indices.push_back(first);
            indices.push_back(second);
            indices.push_back(first + 1);

            indices.push_back(second);
            indices.push_back(second + 1);
            indices.push_back(first + 1);
        }
    }

    // Создание и привязка VAO и VBO
    unsigned int VBO, VAO, EBO;
    glGenVertexArrays(1, &VAO);
    glGenBuffers(1, &VBO);
    glGenBuffers(1, &EBO);

    glBindVertexArray(VAO);

    // Создаем VBO для вершин
    glBindBuffer(GL_ARRAY_BUFFER, VBO);
    glBufferData(GL_ARRAY_BUFFER, sizeof(float) * vertices.size(), vertices.data(), GL_STATIC_DRAW);

    // Создаем EBO для индексов
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, sizeof(unsigned int) * indices.size(), indices.data(), GL_STATIC_DRAW);

    // Привязываем атрибуты для вершин
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(float), (void*)0);  // Позиции
    glEnableVertexAttribArray(0);

    // Привязываем атрибуты для нормалей
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(float), (void*)(3 * sizeof(float)));  // Нормали
    glEnableVertexAttribArray(1);

    // Рисуем сферу с использованием индексов
    glDrawElements(GL_TRIANGLES, indices.size(), GL_UNSIGNED_INT, 0);

    // Очистка
    glBindVertexArray(0);
    glDeleteBuffers(1, &VBO);
    glDeleteBuffers(1, &EBO);
    glDeleteVertexArrays(1, &VAO);
}



// Функция для отрисовки пирамиды
void drawPyramid(float size) {
    float vertices[] = {
        // Bottom face
        -size, -size, -size,  0.0f,  0.0f, -1.0f,
         size, -size, -size,  0.0f,  0.0f, -1.0f,
         size, -size,  size,  0.0f,  0.0f, -1.0f,

        -size, -size, -size,  0.0f,  0.0f, -1.0f,
         size, -size,  size,  0.0f,  0.0f, -1.0f,
        -size, -size,  size,  0.0f,  0.0f, -1.0f,

        // Side faces
        -size, -size, -size,  -1.0f,  1.0f,  0.0f,
         0.0f,  size,  0.0f,  -1.0f,  1.0f,  0.0f,
         size, -size, -size,   1.0f,  1.0f,  0.0f,

         size, -size, -size,   1.0f,  1.0f,  0.0f,
         0.0f,  size,  0.0f,   1.0f,  1.0f,  0.0f,
         size, -size,  size,   1.0f,  1.0f,  0.0f,

         size, -size,  size,   1.0f,  1.0f,  0.0f,
         0.0f,  size,  0.0f,   1.0f,  1.0f,  0.0f,
        -size, -size,  size,  -1.0f,  1.0f,  0.0f,

        -size, -size,  size,  -1.0f,  1.0f,  0.0f,
         0.0f,  size,  0.0f,  -1.0f,  1.0f,  0.0f,
        -size, -size, -size,  -1.0f,  1.0f,  0.0f,
    };

    unsigned int VBO, VAO;
    glGenVertexArrays(1, &VAO);
    glGenBuffers(1, &VBO);
    
    glBindVertexArray(VAO);
    
    glBindBuffer(GL_ARRAY_BUFFER, VBO);
    glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);
    
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(float), (void*)0);
    glEnableVertexAttribArray(0);
    
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(float), (void*)(3 * sizeof(float)));
    glEnableVertexAttribArray(1);
    
    glDrawArrays(GL_TRIANGLES, 0, 18);
    
    glBindVertexArray(0);
    glDeleteBuffers(1, &VBO);
    glDeleteVertexArrays(1, &VAO);
}
