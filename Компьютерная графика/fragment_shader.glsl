#version 330 core
out vec4 FragColor;

in vec3 FragPos;
in vec3 Normal;

uniform vec3 lightDir;
uniform vec3 pointLightPos;
uniform vec3 viewPos;

uniform bool directionalLightOn;
uniform bool pointLightOn;

void main() {
    vec3 result = vec3(0.0);

    // Направленный свет
    if (directionalLightOn) {
        vec3 lightColor = vec3(0.8, 0.8, 0.8);
        vec3 lightDirNormalized = normalize(-lightDir);
        float diff = max(dot(Normal, lightDirNormalized), 0.0);
        result += diff * lightColor;
    }

    // Точечный свет
    if (pointLightOn) {
        vec3 lightColor = vec3(0.8, 0.5, 0.5);
        vec3 lightDir = normalize(pointLightPos - FragPos);
        float diff = max(dot(Normal, lightDir), 0.0);
        result += diff * lightColor;
    }

    FragColor = vec4(result, 1.0);
}
