#version 330 core

out vec4 FragColor;

uniform float focusDist;
uniform float aperture;

const vec3 lightPos = vec3(0.0, 0.0, -2.0);  
const vec3 lightColor = vec3(1.0, 1.0, 1.0);  

struct Sphere {
    vec3 center;
    float radius;
    vec3 color;
};

Sphere spheres[3] = Sphere[3](
    Sphere(vec3(0.0, 0.0, -3.0), 0.6, vec3(1.0, 0.0, 0.0)), // Центральная сфера
    Sphere(vec3(-2.0, 0.0, -8.0), 1.0, vec3(0.0, 1.0, 0.0)),  // Левая сфера
    Sphere(vec3(3.0, 0.0, -12.0), 1.0, vec3(0.0, 0.0, 1.0))   // Правая сфера
);

bool intersectSphere(vec3 ro, vec3 rd, Sphere sphere, out float t) {
    vec3 oc = ro - sphere.center;
    float a = dot(rd, rd);
    float b = 2.0 * dot(oc, rd);
    float c = dot(oc, oc) - sphere.radius * sphere.radius;
    float discriminant = b * b - 4.0 * a * c;

    if (discriminant > 0.0) {
        t = (-b - sqrt(discriminant)) / (2.0 * a);
        return true;
    }
    return false;
}

vec3 sphereNormal(vec3 point, Sphere sphere) {
    return normalize(point - sphere.center);
}

vec3 blur(vec3 color, float t, float focusDist, float aperture) {
    float blurAmount = abs(t - focusDist) * aperture;
    blurAmount = blurAmount * blurAmount; 


    vec3 blurOffset = vec3(blurAmount * 0.1, blurAmount * 0.1, blurAmount * 0.1);
    
    return color - blurOffset;
}

void main() {
    vec3 ro = vec3(0.0, 0.0, 0.0); 
    vec3 rd = normalize(vec3(gl_FragCoord.xy / vec2(800, 600) * 2.0 - 1.0, -1.0));

    vec3 color = vec3(0.0);
    float closestT = 1000.0;
    Sphere hitSphere;
    bool hit = false;

    for (int i = 0; i < 3; i++) {
        float t;
        if (intersectSphere(ro, rd, spheres[i], t) && t < closestT) {
            closestT = t;
            hitSphere = spheres[i];
            hit = true;
        }
    }

    if (hit) {
        vec3 hitPoint = ro + rd * closestT;
        vec3 normal = sphereNormal(hitPoint, hitSphere);
        vec3 lightDir = normalize(lightPos - hitPoint);

        float diff = max(dot(normal, lightDir), 0.0);
        vec3 diffuse = diff * lightColor * hitSphere.color;

        color = blur(diffuse, closestT, focusDist, aperture);
    }

    FragColor = vec4(color, 1.0);
}
