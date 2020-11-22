vertex_shader = """
#version 460
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 normal;
layout (location = 2) in vec2 texcoords;

uniform mat4 theMatrix;
uniform vec3 light;

out float intensity;
out vec2 vertexTexcoords;

void main()
{
	vertexTexcoords = texcoords;
	intensity = dot(normal, normalize(light));
	gl_Position = theMatrix * vec4(position.x, position.y, position.z, 1.0);
}
"""

fragment_shader = """
#version 460
layout(location = 0) out vec4 fragColor;

in float intensity;
in vec2 vertexTexcoords;

uniform sampler2D tex;
uniform vec4 diffuse;
uniform vec4 ambient;

void main()
{

	fragColor = ambient + diffuse * texture(tex, vertexTexcoords) * intensity;
}
"""

vertex_shader = """
#version 460
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 normal;
layout (location = 2) in vec2 texcoords;

uniform mat4 theMatrix;
uniform vec3 light;

out float intensity;
out vec2 vertexTexcoords;
out vec3 lPosition;

void main()
{
	vertexTexcoords = texcoords;
	lPosition = position;
	intensity = dot(normal, normalize(light));
	gl_Position = theMatrix * vec4(position.x, position.y, position.z, 1.0);
}
"""

fragment_shader = """
#version 460
layout(location = 0) out vec4 fragColor;

in float intensity;
in vec2 vertexTexcoords;
in vec3 lPosition;

uniform sampler2D tex;
uniform vec4 diffuse;
uniform vec4 ambient;

void main()
{

	fragColor = vec4(lPosition.x * 5.0, lPosition.y * 8.0, lPosition.z * 5.0, 1.0) * intensity;
}
"""

vertex_shader = """
#version 460
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 normal;
layout (location = 2) in vec2 texcoords;

uniform mat4 theMatrix;
uniform vec3 light;

out float intensity;
out vec2 vertexTexcoords;
out vec3 lPosition;
out vec3 fNormal;

void main()
{
	vertexTexcoords = texcoords;
	lPosition = position;
	fNormal = normal;
	intensity = dot(normal, normalize(light));
	gl_Position = theMatrix * vec4(position.x, position.y, position.z, 1.0);
}
"""

fragment_shader = """
#version 460
layout(location = 0) out vec4 fragColor;

in float intensity;
in vec2 vertexTexcoords;
in vec3 lPosition;
in vec3 fNormal;

uniform sampler2D tex;
uniform vec4 diffuse;
uniform vec4 ambient;

void main()
{
	fragColor = vec4(cross(fNormal, lPosition), 1.0);
}
"""


"""
precision highp float;
uniform float time;
uniform vec2 resolution;
varying vec3 fPosition;
varying vec3 lPosition;
varying vec3 fNormal;

uniform vec2 u_resolution;
uniform vec2 u_mouse;

void main()
{
  /*vec3 light = vec3(-1.0, 0.0, 0.1);
  float intensity = dot(light, fNormal);
  
  gl_FragColor =  vec4(cross(fNormal, lPosition), 1.0);
  
  */
  
  /*vec2 st = gl_FragCoord.xy/20.0;
  vec3 color = vec3(0.0);
    st = fract(st);
	color = vec3(st,0.0);
	gl_FragColor = vec4(color,1.0);*/
  /*vec2 st = gl_FragCoord.xy/20.0;
  vec3 color = vec3(st.x *0.05, st.y + (st.y * 0.05), dot(fNormal,     fPosition) * 3.14);
  gl_FragColor = vec4(color,1.0);*/
  /*float x = gl_FragCoord.x/3.14;
  float a = floor(1.+sin(x*3.14));
  float b = floor(1.+sin((x+1.)*3.14));
  gl_FragColor = vec4( x, a, b, 1.0 );*/
  /*float x = gl_FragCoord.x/5.0;
  float a = floor(1.+sin(x));
  float b = floor(1.+sin((x+1.0)));
  gl_FragColor = vec4( x, a, b, 1.0 );*/
  /*vec3 light = vec3(1, 0.0, 1);
  float intensity = dot(light, fNormal);
  float tiempo = time * 5.0;
  
  float bright =   floor(mod(lPosition.z * tiempo, 5.0) + 1.25);
  vec4 color = mod(bright, 3.0) > .8 ? vec4(1.0, 1.0, 0.0, 1.0) : vec4(1.0, 0.0, 1.0, 1.0);
  
  gl_FragColor =  color * intensity;*/
  
  /*float st = 0.25 * time / 5.0;
  
  vec3 color = vec3(st, fNormal.y * st, lPosition.z - st);

  gl_FragColor = vec4(color , 1.0);*/
  
  //gl_FragColor = vec4(cos(time * 5.0), .5, 0.0, 1.0);
  /*vec2 st = gl_FragCoord.xy/u_resolution.xy;
 gl_FragColor = vec4(st.x, .5, 0.0, 1.0);*/
 
 vec3 light = vec3(-1.0, 0.0, 0.1);
  float intensity = dot(light, fNormal);
  
  //gl_FragColor =  vec4(cross(fNormal, lPosition), 1.0);
 //gl_FragColor = intensity * vec4(cos(time * 0.25), sin(time * 0.14), tan(time * 0.55), 1.0);
 gl_FragColor = intensity * vec4(0.25, sin(time * 5.15), 0.5, 1.0);
}
"""