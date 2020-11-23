import pygame
import numpy
import glm
import pyassimp

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
uniform vec3 light;
uniform vec4 color;
varying int opcion;

out float intensity;
out vec2 vertexTexcoords;
out vec4 vertexColor;
flat out uint selectOpcion;
out vec3 lPosition;

void main()
{
	vertexTexcoords = texcoords;
	selectOpcion = opcion;
	lPosition = position;
	float intensity = dot(normal, normalize(light));
	vertexColor = color * intensity;
	gl_Position = theMatrix * vec4(position.x, position.y, position.z, 1.0);
}
"""

fragment_shader = """
#version 460
layout(location = 0) out vec4 fragColor;

in float intensity;
in vec2 vertexTexcoords;
in vec4 vertexColor;
flat in uint selectOpcion;
in vec3 lPosition;

uniform sampler2D tex;
uniform vec4 diffuse;
uniform vec4 ambient;

void main()
{
	switch (selectOpcion)
	{
		case 0:
			fragColor = texture(tex, vertexTexcoords);
		break;
		case 1:
			fragColor = vec4(lPosition.x * 5.0, lPosition.y * 8.0, lPosition.z * 5.0, 1.0) * intensity;
		break;
		default:
			fragColor = vec4(1.0, 0.0, 0.0, 0.0);
	}
	// fragColor = ambient + diffuse * texture(tex, vertexTexcoords) * intensity;
}
"""

otro_shader = """
#version 460
layout(location = 0) out vec4 fragColor;

in float intensity;
in vec2 vertexTexcoords;
in vec4 vertexColor;
flat in uint selectOpcion;
in vec3 lPosition;

uniform sampler2D tex;
uniform vec4 diffuse;
uniform vec4 ambient;

void main()
{
	fragColor = vec4(lPosition.x * 5.0, lPosition.y * 8.0, lPosition.z * 5.0, 1.0);
}
"""

shader = compileProgram(
		compileShader(vertex_shader, GL_VERTEX_SHADER),
		compileShader(otro_shader, GL_FRAGMENT_SHADER)
)

scene = pyassimp.load('./sofa/ikea-stocksund-sofa.obj')

def glize(node, opcion):
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
			-100, 150, 160
		)

		glUniform4f(
			glGetUniformLocation(shader, "diffuse"),
			1, 1, 1, 1
		)

		diffuse = mesh.material.properties["diffuse"]

		glUniform4f(
			glGetUniformLocation(shader, "color"), * diffuse, 1
		)

		glUniform4f(
			glGetUniformLocation(shader, "ambient"),
			0.2, 0.2, 0.2, 1
		)

		glUniform1i(
			glGetUniformLocation(shader, "opcion"),
			opcion
		)


		glDrawElements(GL_TRIANGLES, len(index_data), GL_UNSIGNED_INT, None)

	for child in node.children:
		glize(child, opcion)




i = glm.mat4()

def createTheMatrix(counter, x, y):
	translate = glm.translate(i, glm.vec3(0, -100, 0))
	rotate = glm.rotate(i, glm.radians(counter), glm.vec3(0, 1, 0))
	scale = glm.scale(i, glm.vec3(2, 2, 2))

	model = translate * rotate * scale
	view = glm.lookAt(glm.vec3(0 + x, 0 + y, 500), glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))
	projection = glm.perspective(glm.radians(45), 800/600, 0.1, 1000)

	return projection * view * model

glViewport(0, 0, 800, 600)

glEnable(GL_DEPTH_TEST)

running = True
paused = True
counter = 0
x = 0
y = 0
opcion = 1
while running:
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glClearColor(0.04, 0.37, 0.89, 1.0)

	glUseProgram(shader)

	theMatrix = createTheMatrix(counter, x, y)

	theMatrixLocation = glGetUniformLocation(shader, 'theMatrix')

	glUniformMatrix4fv(
		theMatrixLocation, # location
		1, # count
		GL_FALSE,
		glm.value_ptr(theMatrix)
	)

	# glDrawArrays(GL_TRIANGLES, 0, 3)
	# glDrawElements(GL_TRIANGLES, 36, GL_UNSIGNED_INT, None)

	glize(scene.rootnode, opcion)

	pygame.display.flip()

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.KEYDOWN:
			#print('keydown')
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
			if event.key == pygame.K_a:
				shader = compileProgram(
						compileShader(vertex_shader, GL_VERTEX_SHADER),
						compileShader(fragment_shader, GL_FRAGMENT_SHADER)
				)
				glUseProgram(shader)
			if event.key == pygame.K_b:
				shader = compileProgram(
						compileShader(vertex_shader, GL_VERTEX_SHADER),
						compileShader(otro_shader, GL_FRAGMENT_SHADER)
				)
				glUseProgram(shader)

	if not paused:
		counter += 1
	
	clock.tick(30)