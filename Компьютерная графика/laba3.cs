using OpenTK;
using OpenTK.Graphics.OpenGL;
using OpenTK.Input;
using OpenTK.Mathematics;
using OpenTK.Windowing.Common;
using OpenTK.Windowing.Desktop;
using OpenTK.Windowing.GraphicsLibraryFramework;
using System;

namespace komp_graphika_3
{
    class Game : GameWindow
    {
        private Vector3[] cameraPositions;
        private int currentCameraPositionIndex = 0;
        private float cameraSpeed = 1.0f; // Скорость перехода камеры
        private Vector3 cameraPosition;

        private float rotationX = 0.0f;
        private float rotationY = 0.0f;
        private float rotationZ = 0.0f;
        private float scale = 1f;

        private float[] vertices = {
            // Позиции          //Normals
            -0.5f, -0.5f,  0.5f,  0f,  0f,  1f,
             0.5f, -0.5f,  0.5f,  0f,  0f,  1f,
             0.5f,  0.5f,  0.5f,  0f,  0f,  1f,
            -0.5f,  0.5f,  0.5f,  0f,  0f,  1f,

            -0.5f, -0.5f, -0.5f,  0f,  0f, -1f,
             0.5f, -0.5f, -0.5f,  0f,  0f, -1f,
             0.5f,  0.5f, -0.5f,  0f,  0f, -1f,
            -0.5f,  0.5f, -0.5f,  0f,  0f, -1f,

            -0.5f, -0.5f, -0.5f, -1f,  0f,  0f,
            -0.5f,  0.5f, -0.5f, -1f,  0f,  0f,
            -0.5f,  0.5f,  0.5f, -1f,  0f,  0f,
            -0.5f, -0.5f,  0.5f, -1f,  0f,  0f,

             0.5f, -0.5f, -0.5f,  1f,  0f,  0f,
             0.5f,  0.5f, -0.5f,  1f,  0f,  0f,
             0.5f,  0.5f,  0.5f,  1f,  0f,  0f,
             0.5f, -0.5f,  0.5f,  1f,  0f,  0f,

            -0.5f, -0.5f, -0.5f,  0f, -1f,  0f,
             0.5f, -0.5f, -0.5f,  0f, -1f,  0f,
             0.5f, -0.5f,  0.5f,  0f, -1f,  0f,
            -0.5f, -0.5f,  0.5f,  0f, -1f,  0f,

            -0.5f,  0.5f, -0.5f,  0f,  1f,  0f,
             0.5f,  0.5f, -0.5f,  0f,  1f,  0f,
             0.5f,  0.5f,  0.5f,  0f,  1f,  0f,
            -0.5f,  0.5f,  0.5f,  0f,  1f,  0f
        };

        private uint[] indices = {
            0, 1, 2, 2, 3, 0,   // Передняя грань
            4, 5, 6, 6, 7, 4,   // Задняя грань
            8, 9, 10, 10, 11, 8, // Левая грань
            12, 13, 14, 14, 15, 12, // Правая грань
            16, 17, 18, 18, 19, 16, // Нижняя грань
            20, 21, 22, 22, 23, 20  // Верхняя грань
        };

        private int Vbo;
        private int Ebo;
        private int Vao;

        private Vector3 lightPosition = new Vector3(1f, 1f, 1f);
        private Vector3 lightColor = new Vector3(1f, 1f, 1f);
        private Vector3 ambientColor = new Vector3(0.1f, 0.1f, 0.1f);

        public Game(GameWindowSettings gameWindowSettings, NativeWindowSettings nativeWindowSettings)
            : base(gameWindowSettings, nativeWindowSettings)
        {
            // Определяем позиции камеры
            cameraPositions = new Vector3[]
            {
                new Vector3(0, 0, -5),
                new Vector3(2, 2, -7),
                new Vector3(-3, 1, -8),
                new Vector3(0, 3, -3)
            };
            cameraPosition = cameraPositions[currentCameraPositionIndex];
        }

        protected override void OnLoad()
        {
            base.OnLoad();
            GL.ClearColor(0.2f, 0.3f, 0.3f, 1.0f);
            GL.Enable(EnableCap.DepthTest);

            Vao = GL.GenVertexArray();
            Vbo = GL.GenBuffer();
            Ebo = GL.GenBuffer();

            GL.BindVertexArray(Vao);

            GL.BindBuffer(BufferTarget.ArrayBuffer, Vbo);
            GL.BufferData(BufferTarget.ArrayBuffer, vertices.Length * sizeof(float), vertices, BufferUsageHint.StaticDraw);

            GL.BindBuffer(BufferTarget.ElementArrayBuffer, Ebo);
            GL.BufferData(BufferTarget.ElementArrayBuffer, indices.Length * sizeof(uint), indices, BufferUsageHint.StaticDraw);

            GL.VertexAttribPointer(0, 3, VertexAttribPointerType.Float, false, 6 * sizeof(float), 0);
            GL.EnableVertexAttribArray(0);

            GL.VertexAttribPointer(1, 3, VertexAttribPointerType.Float, false, 6 * sizeof(float), 3 * sizeof(float));
            GL.EnableVertexAttribArray(1);

            GL.BindBuffer(BufferTarget.ArrayBuffer, 0);
            GL.BindVertexArray(0);
        }

        protected override void OnUpdateFrame(FrameEventArgs e)
        {
            base.OnUpdateFrame(e);

            // Управление сменой позиции камеры
            if (KeyboardState.IsKeyDown(Keys.Space)) // Нажатие пробела меняет позицию камеры
            {
                currentCameraPositionIndex = (currentCameraPositionIndex + 1) % cameraPositions.Length;
            }

            // Плавный переход камеры
            cameraPosition = Vector3.Lerp(cameraPosition, cameraPositions[currentCameraPositionIndex], cameraSpeed * (float)e.Time);

            // Управление скоростью перехода
            if (KeyboardState.IsKeyDown(Keys.R)) cameraSpeed += 0.01f; // Увеличение скорости
            if (KeyboardState.IsKeyDown(Keys.T)) cameraSpeed -= 0.01f; // Уменьшение скорости
            cameraSpeed = Math.Clamp(cameraSpeed, 0.01f, 5.0f); // Ограничение скорости

            // Управление вращением
            if (KeyboardState.IsKeyDown(Keys.Left)) rotationY -= 0.01f;
            if (KeyboardState.IsKeyDown(Keys.Right)) rotationY += 0.01f;
            if (KeyboardState.IsKeyDown(Keys.Up)) rotationX -= 0.01f;
            if (KeyboardState.IsKeyDown(Keys.Down)) rotationX += 0.01f;
            if (KeyboardState.IsKeyDown(Keys.W)) scale *= 1.01f;
            if (KeyboardState.IsKeyDown(Keys.S)) scale /= 1.01f;
        }

        protected override void OnRenderFrame(FrameEventArgs e)
        {
            base.OnRenderFrame(e);
            GL.Clear(ClearBufferMask.ColorBufferBit | ClearBufferMask.DepthBufferBit);

            Matrix4 modelMatrix = Matrix4.CreateScale(scale) *
                                  Matrix4.CreateRotationX(rotationX) *
                                  Matrix4.CreateRotationY(rotationY) *
                                  Matrix4.CreateRotationZ(rotationZ);

            var viewMatrix = Matrix4.CreateTranslation(cameraPosition);
            var projectionMatrix = Matrix4.CreatePerspectiveFieldOfView(MathHelper.DegreesToRadians(45), (float)Size.X / Size.Y, 0.1f, 100f);

            GL.MatrixMode(MatrixMode.Modelview);
            GL.LoadMatrix(ref viewMatrix);
            GL.MultMatrix(ref modelMatrix);
            GL.MatrixMode(MatrixMode.Projection);
            GL.LoadMatrix(ref projectionMatrix);

            // Устанавливаем цвет в зависимости от нормалей и позиции света
            GL.Begin(PrimitiveType.Triangles);
            for (int i = 0; i < indices.Length; i++)
            {
                int index = (int)indices[i];
                float normalX = vertices[index * 6 + 3];
                float normalY = vertices[index * 6 + 4];
                float normalZ = vertices[index * 6 + 5];

                Vector3 normal = new Vector3(normalX, normalY, normalZ);
                Vector3 vertex = new Vector3(vertices[index * 6 + 0], vertices[index * 6 + 1], vertices[index * 6 + 2]);

                Vector3 lightDir = Vector3.Normalize(lightPosition - vertex);
                float diff = Math.Max(Vector3.Dot(normal, lightDir), 0.0f);
                Vector3 color = ambientColor + diff * lightColor;

                GL.Color3(color.X, color.Y, color.Z);
                GL.Normal3(normal);
                GL.Vertex3(vertex);
            }
            GL.End();

            SwapBuffers();
        }
    }

    class Program
    {
        static void Main(string[] args)
        {
            var gameWindowSettings = GameWindowSettings.Default;
            var nativeWindowSettings = new NativeWindowSettings()
            {
                ClientSize = new Vector2i(800, 600),
                Title = "3D Scene with Camera Control"
            };

            using (var game = new Game(gameWindowSettings, nativeWindowSettings))
            {
                game.Run();
            }
        }
    }
}