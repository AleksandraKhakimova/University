using OpenTK.Graphics.OpenGL4;
using OpenTK.Mathematics;
using OpenTK.Windowing.Common;
using OpenTK.Windowing.Desktop;
using OpenTK.Windowing.GraphicsLibraryFramework;

namespace kompgraphika1 // Определяем пространство имен
{
    class Program
    {
        static void Main(string[] args)
        {
            // Настройки для игрового окна
            var gameWindowSettings = GameWindowSettings.Default; // Используем стандартные настройки окна

            // Настройки для нативного окна
            var nativeWindowSettings = new NativeWindowSettings()
            {
                ClientSize = new Vector2i(800, 600), // размер окна 800x600 пикселей
                Title = "Cubic Bezier Curve" // заголовок окна
            };

            // Создание и запуск экземпляра класса Game
            using (var game = new Game(gameWindowSettings, nativeWindowSettings)) // Создаем объект игры и используем его в блоке using для автоматического освобождения ресурсов
            {
                game.Run();
            }
        }
    }

    public class Game : GameWindow
    {
        // Шейдеры
        private int shaderProgram;
        private int Vbo; // Vertex Buffer Object
        private int Vao; // Vertex Array Object

        // Параметры для трансформаций
        private Matrix4 modelMatrix; // Модельная матрица для трансформаций
        private Vector2 position; // Позиция объекта
        private float scale = 1.0f; // Масштаб объекта

        private const int POINT_COUNT = 100; // Количество точек на кривой Безье

        // Контрольные точки для кубической кривой Безье
        private Vector2[] controlPoints = new Vector2[]
        {
            new Vector2(-0.5f, -0.5f),
            new Vector2(-0.2f, 0.5f),
            new Vector2(0.2f, -0.5f),
            new Vector2(0.5f, 0.5f)
        };

        public Game(GameWindowSettings gameWindowSettings, NativeWindowSettings nativeWindowSettings)
            : base(gameWindowSettings, nativeWindowSettings) // Конструктор базового класса GameWindow
        {
        }

        protected override void OnLoad() // Метод, вызываемый при загрузке окна
        {
            base.OnLoad(); // Вызываем метод базового класса
            GL.ClearColor(0.1f, 0.3f, 0.4f, 1.0f); // Устанавливаем цвет фона (темно-синий)

            // Инициализация шейдеров
            shaderProgram = CreateShaderProgram(); // Создаем шейдерную программу

            Vao = GL.GenVertexArray(); // Создаем Vertex Array Object
            Vbo = GL.GenBuffer(); // Создаем Vertex Buffer Object

            GL.BindVertexArray(Vao); // Привязываем VAO
            GL.BindBuffer(BufferTarget.ArrayBuffer, Vbo); // Привязываем VBO

            // Определяем формат данных вершин
            GL.VertexAttribPointer(0, 2, VertexAttribPointerType.Float, false, 2 * sizeof(float), 0);
            GL.EnableVertexAttribArray(0);

            // Инициализация трансформаций
            modelMatrix = Matrix4.Identity; // Устанавливаем модельную матрицу в единичную
            position = new Vector2(0.0f, 0.0f); // Начальная позиция

            UpdateBezierCurve();
        }

        protected override void OnRenderFrame(FrameEventArgs args) // отрисовка кадра
        {
            base.OnRenderFrame(args);
            GL.Clear(ClearBufferMask.ColorBufferBit); // Очистка экрана

            // Используем шейдерную программу
            GL.UseProgram(shaderProgram);

            // Обновляем модельную матрицу с учетом перемещения и масштабирования
            modelMatrix = Matrix4.CreateScale(scale) * Matrix4.CreateTranslation(position.X, position.Y, 0.0f);

            // Отправляем матрицу в шейдер
            int modelMatrixLocation = GL.GetUniformLocation(shaderProgram, "uModel"); // Получаем расположение униформы модели
            GL.UniformMatrix4(modelMatrixLocation, false, ref modelMatrix); // Устанавливаем модельную матрицу в шейдер

            // Отрисовка кривой Безье
            GL.BindVertexArray(Vao); 
            GL.DrawArrays(PrimitiveType.LineStrip, 0, POINT_COUNT); 

            // Отрисовка контрольных точек
            GL.PointSize(10.0f);
            GL.DrawArrays(PrimitiveType.Points, 0, controlPoints.Length);

            SwapBuffers(); // Переключаем буферы для отображения результата на экране
        }

        protected override void OnUpdateFrame(FrameEventArgs args) // обновление состояния игры
        {
            base.OnUpdateFrame(args);

            // Перемещение контрольных точек при нажатии клавиш
            if (KeyboardState.IsKeyDown(Keys.Up))
                controlPoints[1].Y += 0.01f;
            if (KeyboardState.IsKeyDown(Keys.Down))
                controlPoints[1].Y -= 0.01f;
            if (KeyboardState.IsKeyDown(Keys.Left))
                controlPoints[1].X -= 0.01f;
            if (KeyboardState.IsKeyDown(Keys.Right))
                controlPoints[1].X += 0.01f;

            UpdateBezierCurve();
        }

        // Обновляем вершины для отображения кривой Безье.
        private void UpdateBezierCurve()
        {
            float[] bezierVertices = new float[POINT_COUNT * 2]; // Создаем массив для хранения координат вершины прямой
            for (int i = 0; i < POINT_COUNT; i++)
            {
                float t = (float)i / (POINT_COUNT - 1);
                Vector2 point = CalculateBezierPoint(t, controlPoints); // Функция CalculateBezierPoint используется для расчета точки кривой на заданной позиции t с использованием контрольных точек.

                // Полученные координаты точки записываются в массив bezierVertices.
                bezierVertices[2 * i] = point.X;
                bezierVertices[2 * i + 1] = point.Y;
            }

            // данные bezierVertices загружаются в буфер
            GL.BindBuffer(BufferTarget.ArrayBuffer, Vbo);
            GL.BufferData(BufferTarget.ArrayBuffer, bezierVertices.Length * sizeof(float), bezierVertices, BufferUsageHint.DynamicDraw);
        }

        private Vector2 CalculateBezierPoint(float t, Vector2[] points)
        {
            float u = 1 - t;
            float tt = t * t;
            float uu = u * u;
            float uuu = uu * u;
            float ttt = tt * t;

            Vector2 p = uuu * points[0];
            p += 3 * uu * t * points[1];
            p += 3 * u * tt * points[2];
            p += ttt * points[3];

            return p;
        }

        private int CreateShaderProgram() // Метод для создания шейдерной программы
        {
            // Вершинный шейдер
            const string vertexShaderSource = @"
                #version 330 core
                layout (location = 0) in vec2 aPosition;
                uniform mat4 uModel;
                void main()
                {
                    gl_Position = uModel * vec4(aPosition, 0.0, 1.0);
                }
            ";

            // Фрагментный шейдер
            const string fragmentShaderSource = @"
                #version 330 core
                out vec4 FragColor;
                void main()
                {
                    FragColor = vec4(1.0, 1.0, 1.0, 1.0);
                }
            ";

            // Компиляция шейдеров
            int vertexShader = GL.CreateShader(ShaderType.VertexShader); // Создаем вершинный шейдер
            GL.ShaderSource(vertexShader, vertexShaderSource); // Устанавливаем исходный код шейдера
            GL.CompileShader(vertexShader); // Компилируем шейдер
            CheckShaderCompileStatus(vertexShader); // Проверяем статус компиляции

            int fragmentShader = GL.CreateShader(ShaderType.FragmentShader); // Создаем фрагментный шейдер
            GL.ShaderSource(fragmentShader, fragmentShaderSource); // Устанавливаем исходный код шейдера
            GL.CompileShader(fragmentShader); // Компилируем шейдер
            CheckShaderCompileStatus(fragmentShader); // Проверяем статус компиляции

            // Линковка шейдерной программы
            int shaderProgram = GL.CreateProgram(); // Создаем шейдерную программу
            GL.AttachShader(shaderProgram, vertexShader); // Прикрепляем вершинный шейдер
            GL.AttachShader(shaderProgram, fragmentShader); // Прикрепляем фрагментный шейдер
            GL.LinkProgram(shaderProgram); // Линкуем шейдерную программу
            CheckProgramLinkStatus(shaderProgram); // Проверяем статус линковки

            // Удаление шейдеров после линковки
            GL.DeleteShader(vertexShader); // Удаляем вершинный шейдер
            GL.DeleteShader(fragmentShader); // Удаляем фрагментный шейдер

            return shaderProgram; // Возвращаем идентификатор шейдерной программы
        }

        private void CheckShaderCompileStatus(int shader) // проверка статуса компиляции шейдера
        {
            GL.GetShader(shader, ShaderParameter.CompileStatus, out int status); // Получаем статус компиляции
            if (status == 0) // Если статус не успешен
            {
                string infoLog = GL.GetShaderInfoLog(shader); // Получаем лог ошибок
                throw new System.Exception($"Ошибка компиляции шейдера: {infoLog}"); // Выбрасываем исключение с логом ошибок
            }
        }

        private void CheckProgramLinkStatus(int program) // проверка статуса линковки программы
        {
            GL.GetProgram(program, GetProgramParameterName.LinkStatus, out int status); // Получаем статус линковки
            if (status == 0) // Если статус не успешен
            {
                string infoLog = GL.GetProgramInfoLog(program); // Получаем лог ошибок
                throw new System.Exception($"Ошибка линковки шейдерной программы: {infoLog}"); // Выбрасываем исключение с логом ошибок
            }
        }
    }
}