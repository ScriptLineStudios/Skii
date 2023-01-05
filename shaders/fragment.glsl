#version 330 core

in vec3 fragmentColor;
in vec2 fragmentTexCoord;

out vec4 color;

uniform sampler2D imageTexture;
uniform float falloff = 0.1;
uniform float amount = 1.1;

void main() {
    vec4 _color = texture2D(imageTexture, fragmentTexCoord);
    float dist = distance(fragmentTexCoord, vec2(0.5, 0.5));
    _color.rgb *= smoothstep(0.8, falloff * 0.799, dist * (amount + falloff));

    color = _color;
}