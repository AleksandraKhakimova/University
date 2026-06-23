APP_NAME = myApp
BUILD_DIR = ./bin
C_FILES = $(wildcard ./src/*.c)
CXX_FILES = $(wildcard ./src/*.cpp)  # Добавление всех C++ файлов
SOURCES = $(C_FILES) $(CXX_FILES) main.cpp

# Параметры компиляции
CXX = clang++
CXXFLAGS = -Wall -Wextra -std=c++17 \
            -I/opt/homebrew/opt/glew/include\
            -I/opt/homebrew/opt/glfw/include \
            -I/opt/homebrew/Cellar/glm/1.0.1/include/glm

LDFLAGS = -L/opt/homebrew/lib -lGLEW -lglfw -F/Library/Frameworks -framework OpenGL

TARGET = $(BUILD_DIR)/$(APP_NAME)

# Цель, чтобы собрать все файлы
all: $(TARGET)

# Цель для компиляции
$(TARGET): $(SOURCES)
	@mkdir -p $(BUILD_DIR)  # Создайте каталог сборки, если он не существует
	$(CXX) $(CXXFLAGS) $^ -o $@ $(LDFLAGS)

# Цель для очистки
clean:
	rm -f $(TARGET)