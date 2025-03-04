'''
Diana Ximena de León Figueroa
Carne 18607
Graficas por Computadora
Proyecto # 4
23 de noviembre
'''

import pygame
import numpy
import glm
import pyassimp
import time

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

pygame.init()
screen = pygame.display.set_mode((800, 600), pygame.OPENGL | pygame.DOUBLEBUF)
clock = pygame.time.Clock()

vertex_shader = """
#version 460
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 normal;
layout (location = 2) in vec2 texcoords;

uniform mat4 theMatrix;
uniform mat4 normalMatrix;
uniform vec3 light;
uniform float timer;

out float intensity;
out float intensity2;
out vec2 vertexTexcoords;
out vec3 lPosition;
out vec4 fNormal;
out float time;

void main()
{	
	vertexTexcoords = texcoords;
	lPosition = position;
	time = timer;
	fNormal = normalize(normalMatrix * vec4(normal, 1.0));
	intensity2 = dot(vec4(light, 1.0), fNormal);
	intensity = dot(normal, normalize(light));
	gl_Position = theMatrix * vec4(position.x, position.y, position.z, 1.0);
}
"""

fragment_shader = """
#version 460
layout(location = 0) out vec4 fragColor;

in float intensity;
in float intensity2;
in vec2 vertexTexcoords;
in vec3 lPosition;
in vec4 fNormal;
in float time;

uniform sampler2D tex;
uniform vec4 diffuse;
uniform vec4 ambient;

void main()
{
	fragColor = texture(tex, vertexTexcoords);
}
"""

otro_shader = """
#version 460
layout(location = 0) out vec4 fragColor;

in float intensity;
in float intensity2;
in vec2 vertexTexcoords;
in vec3 lPosition;
in vec4 fNormal;
in float time;

uniform sampler2D tex;
uniform vec4 diffuse;
uniform vec4 ambient;

void main()
{
	fragColor = vec4(lPosition.x * 5.0, lPosition.y * 8.0, lPosition.z * 5.0, 1.0) * intensity;
}
"""

time_shader = """
#version 460
layout(location = 0) out vec4 fragColor;

in float intensity;
in float intensity2;
in vec2 vertexTexcoords;
in vec3 lPosition;
in vec4 fNormal;
in float time;

uniform sampler2D tex;
uniform vec4 diffuse;
uniform vec4 ambient;

void main()
{
	gl_FragColor = intensity * vec4(cos(time * 5.0), sin(time * 2.0), tan(time * 3.0), 1.0);
}
"""

impact_shader = """
#version 460
layout(location = 0) out vec4 fragColor;

in float intensity;
in float intensity2;
in vec2 vertexTexcoords;
in vec3 lPosition;
in vec4 fNormal;
in float time;

uniform sampler2D tex;
uniform vec4 diffuse;
uniform vec4 ambient;

void main()
{
	float bright =   floor(mod(lPosition.z * time, 5.0) + 1.25);
	gl_FragColor =  mod(bright, 3.0) > .8 ? vec4(1.0, 1.0, 0.0, 1.0) * intensity2 : vec4(1.0, 0.0, 1.0, 1.0) * intensity2;
}
"""

cuadrado_shader = """
#version 460
layout(location = 0) out vec4 fragColor;

in float intensity;
in float intensity2;
in vec2 vertexTexcoords;
in vec3 lPosition;
in vec4 fNormal;
in float time;

uniform sampler2D tex;
uniform vec4 diffuse;
uniform vec4 ambient;

void main()
{
	vec2 st = gl_FragCoord.xy/20.0;
	vec3 color = vec3(0.0);
    st = fract(st);
	color = vec3(st,0.0);
	gl_FragColor = vec4(color,1.0) * intensity2;
}
"""

multicolor_shader = """
#version 460
layout(location = 0) out vec4 fragColor;

in float intensity;
in float intensity2;
in vec2 vertexTexcoords;
in vec3 lPosition;
in vec4 fNormal;
in float time;

uniform sampler2D tex;
uniform vec4 diffuse;
uniform vec4 ambient;

void main()
{
	gl_FragColor =  vec4(cross(vec3(fNormal.x, fNormal.y, fNormal.z), lPosition), 1.0);
}
"""

# El siguiente shader fue extraido de https://graphics.cs.wisc.edu/WP/cs559-sp2016/2016/03/08/glsl-shader-examples/

siren_shader = """
#version 460
layout(location = 0) out vec4 fragColor;

in float intensity;
in float intensity2;
in vec2 vertexTexcoords;
in vec3 lPosition;
in vec4 fNormal;
in float time;

uniform sampler2D tex;
uniform vec4 diffuse;
uniform vec4 ambient;

void main()
{
	vec3 color = vec3(0.0, 0.0, 0.0);
	
	if( abs(mod( abs(lPosition.x), abs(.2 * sin(time * 10.0) )   )) < .1){
		color.x = 1.0;
	}
	
	
	if( abs(mod(lPosition.z, .2 * sin(time * 10.0 + 1.0))) < .1){
		color.z = 1.0;
	}
	gl_FragColor = vec4(color, 1.0) * intensity2;
}
"""

shader = compileProgram(
		compileShader(vertex_shader, GL_VERTEX_SHADER),
		compileShader(otro_shader, GL_FRAGMENT_SHADER)
)

scene = pyassimp.load('./sofa/ikea-stocksund-sofa.obj')

def glize(node):
	# render
	for mesh in node.meshes:
		material = dict(mesh.material.properties.items())
		try:
			texture_name = material['file']
			texture_surface = pygame.image.load('./sofa/'+ texture_name)
			texture_data = pygame.image.tostring(texture_surface, 'RGB')
			width = texture_surface.get_width()
			height = texture_surface.get_height()

			texture = glGenTextures(1)
			glBindTexture(GL_TEXTURE_2D, texture)
			glTexImage2D(
				GL_TEXTURE_2D,
				0,
				GL_RGB,
				width,
				height,
				0,
				GL_RGB,
				GL_UNSIGNED_BYTE,
				texture_data
			)
			glGenerateMipmap(GL_TEXTURE_2D)
		except:
			pass
		
		vertex_data = numpy.hstack([
			numpy.array(mesh.vertices, dtype=numpy.float32),
			numpy.array(mesh.normals, dtype=numpy.float32),
			numpy.array(mesh.texturecoords[0], dtype=numpy.float32),
		])

		index_data = numpy.hstack(
			numpy.array(mesh.faces, dtype=numpy.int32),
		)

		vertex_buffer_object = glGenVertexArrays(1)
		glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer_object)
		glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_STATIC_DRAW)

		glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 9 * 4, ctypes.c_void_p(0))
		glEnableVertexAttribArray(0)
		glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 9 * 4, ctypes.c_void_p(3 * 4))
		glEnableVertexAttribArray(1)
		glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 9 * 4, ctypes.c_void_p(6 * 4))
		glEnableVertexAttribArray(2)

		element_buffer_object = glGenBuffers(1)
		glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, element_buffer_object)
		glBufferData(GL_ELEMENT_ARRAY_BUFFER, index_data.nbytes, index_data, GL_STATIC_DRAW)


		glUniform3f(
			glGetUniformLocation(shader, "light"),
			-100, 300, 0
		)

		glUniform4f(
			glGetUniformLocation(shader, "diffuse"),
			1, 1, 1, 1
		)

		glUniform4f(
			glGetUniformLocation(shader, "ambient"),
			0.2, 0.2, 0.2, 1
		)

		glDrawElements(GL_TRIANGLES, len(index_data), GL_UNSIGNED_INT, None)

	for child in node.children:
		glize(child)


i = glm.mat4()

def createTheMatrix(counter, x, y):
	translate = glm.translate(i, glm.vec3(0, -100, 0))
	rotate = glm.rotate(i, glm.radians(counter), glm.vec3(0, 1, 0))
	scale = glm.scale(i, glm.vec3(2, 2, 2))

	model = translate * rotate * scale
	view = glm.lookAt(glm.vec3(0 + x, 0 + y, 500), glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))
	projection = glm.perspective(glm.radians(45), 800/600, 0.1, 1000)
	modelView = view * model
	return glm.transpose(glm.inverse(modelView)), projection * modelView

glViewport(0, 0, 800, 600)

glEnable(GL_DEPTH_TEST)

running = True
paused = True
counter = 45
x = 0
y = 0
tiempo = 0
while running:
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glClearColor(0.0, 0.0, 0.0, 1.0)

	glUseProgram(shader)

	normalMatrix, theMatrix = createTheMatrix(counter, x, y)

	theMatrixLocation = glGetUniformLocation(shader, 'theMatrix')

	glUniformMatrix4fv(
		theMatrixLocation, # location
		1, # count
		GL_FALSE,
		glm.value_ptr(theMatrix)
	)

	normalMatrixLocation = glGetUniformLocation(shader, 'normalMatrix')

	glUniformMatrix4fv(
		normalMatrixLocation, # location
		1, # count
		GL_FALSE,
		glm.value_ptr(normalMatrix)
	)
	
	tiempo += 0.5
	
	glUniform1f(
		glGetUniformLocation(shader, 'timer'),
		tiempo
	)

	# glDrawArrays(GL_TRIANGLES, 0, 3)
	# glDrawElements(GL_TRIANGLES, 36, GL_UNSIGNED_INT, None)

	glize(scene.rootnode)

	pygame.display.flip()

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_w:
				glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
			if event.key == pygame.K_f:
				glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
			if event.key == pygame.K_LEFT:
				x -= 10
			if event.key == pygame.K_RIGHT:
				x += 10
			if event.key == pygame.K_UP:
				y += 10
			if event.key == pygame.K_DOWN:
				y -= 10
			if event.key == pygame.K_SPACE:
				paused = not paused
			if event.key == pygame.K_0:
				shader = compileProgram(
						compileShader(vertex_shader, GL_VERTEX_SHADER),
						compileShader(otro_shader, GL_FRAGMENT_SHADER)
				)
				glUseProgram(shader)
			if event.key == pygame.K_1:
				shader = compileProgram(
						compileShader(vertex_shader, GL_VERTEX_SHADER),
						compileShader(fragment_shader, GL_FRAGMENT_SHADER)
				)
				glUseProgram(shader)
			if event.key == pygame.K_2:
				shader = compileProgram(
						compileShader(vertex_shader, GL_VERTEX_SHADER),
						compileShader(time_shader, GL_FRAGMENT_SHADER)
				)
				glUseProgram(shader)
			if event.key == pygame.K_3:
				shader = compileProgram(
						compileShader(vertex_shader, GL_VERTEX_SHADER),
						compileShader(impact_shader, GL_FRAGMENT_SHADER)
				)
				glUseProgram(shader)
			if event.key == pygame.K_4:
				shader = compileProgram(
						compileShader(vertex_shader, GL_VERTEX_SHADER),
						compileShader(cuadrado_shader, GL_FRAGMENT_SHADER)
				)
				glUseProgram(shader)
			if event.key == pygame.K_5:
				shader = compileProgram(
						compileShader(vertex_shader, GL_VERTEX_SHADER),
						compileShader(multicolor_shader, GL_FRAGMENT_SHADER)
				)
				glUseProgram(shader)
			if event.key == pygame.K_6:
				shader = compileProgram(
						compileShader(vertex_shader, GL_VERTEX_SHADER),
						compileShader(siren_shader, GL_FRAGMENT_SHADER)
				)
				glUseProgram(shader)

	if not paused:
		counter += 1
	
	clock.tick(30)