#!/usr/bin/python3
import pathlib
import sys
import os
import numpy as np
import cv2
import pygame
from OpenGL.GL import glReadPixels, GL_RGB, GL_UNSIGNED_BYTE
from core_ext.texture import Texture
from material.texture import TextureMaterial

# Get the package directory
package_dir = str(pathlib.Path(__file__).resolve().parents[2])
# Add the package directory into sys.path if necessary
if package_dir not in sys.path:
    sys.path.insert(0, package_dir)

from core.base import Base
from core_ext.camera import Camera
from core_ext.mesh import Mesh
from core_ext.renderer import Renderer
from core_ext.scene import Scene
from geometry.sphere import SphereGeometry
from material.material import Material

class MovementMatrix:
    """ Clase para manejar matrices de movimiento para objetos """
    def __init__(self, initial_position, speed):
        self.position = np.array(initial_position)
        self.speed = speed
        self.rotation_angle = 0

    def update_position(self):
        # Actualizar la posición en el eje Y para movimiento vertical
        self.position[1] += self.speed

        # Invertir la dirección si llega a un límite (rebote)
        if self.position[1] > 10 or self.position[1] < -10:
            self.speed = -self.speed

        # Crear la matriz de traslación
        translation_matrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, self.speed],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

        # Crear la matriz de rotación (rotación en el eje Y)
        angle = 0.01  # Ángulo de rotación
        rotation_y_matrix = np.array([
            [np.cos(angle), 0, np.sin(angle), 0],
            [0, 1, 0, 0],
            [-np.sin(angle), 0, np.cos(angle), 0],
            [0, 0, 0, 1]
        ])

        # Actualizar la posición mediante la multiplicación de las matrices
        self.position = np.dot(translation_matrix, self.position)
        self.position = np.dot(rotation_y_matrix, self.position)

        return self.position

class ImageSaver:
    """ Clase para guardar imágenes a partir de una escena """
    def __init__(self, fps, seconds, output_dir):
        self.fps = fps
        self.seconds = seconds
        self.output_dir = output_dir
        self.frame_count = 0
        self.total_frames = fps * seconds

        # Crear el directorio si no existe
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def save_frame(self, width, height):
        if self.frame_count < self.total_frames:
            # Leer los píxeles de la ventana actual
            frame = glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE)
            frame = np.frombuffer(frame, dtype=np.uint8).reshape(height, width, 3)
            frame = np.flipud(frame)  # Invertir la imagen verticalmente
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            file_name = os.path.join(self.output_dir, f"frame_{self.frame_count:04d}.png")
            cv2.imwrite(file_name, frame)
            self.frame_count += 1

# Modificación en la clase Example para usar MovementMatrix y ImageSaver

class Example(Base):
    """ Render spinning spheres with gradient colors and vertical movement """
    def initialize(self):
        print("Initializing program...")
        self.renderer = Renderer()
        self.scene = Scene()
        self.camera = Camera(aspect_ratio=800/600)
        self.camera.set_position([0, 0, 25])
        
        # Crear la primera esfera (tierra)
        geometry = SphereGeometry(radius=3)
        material = TextureMaterial(texture=Texture(file_name="images/tierra.jpg"))
        self.mesh = Mesh(geometry, material)
        self.scene.add(self.mesh)
        
        # Crear la segunda esfera (luna)
        geometry2 = SphereGeometry(radius=3)
        material2 = TextureMaterial(texture=Texture(file_name="images/luna.jpg"))
        self.mesh2 = Mesh(geometry2, material2)
        self.scene.add(self.mesh2)

        # Inicializar matrices de movimiento para cada esfera
        self.movement1 = MovementMatrix([9, 0, 0, 1], 0.1)
        self.movement2 = MovementMatrix([-9, 0, 0, 1], 0.03)

        # Inicializar ImageSaver para guardar imágenes
        self.image_saver = ImageSaver(fps=24, seconds=5, output_dir="output_frames")

    def update(self):
        # Actualizar posiciones de las esferas
        position1 = self.movement1.update_position()
        position2 = self.movement2.update_position()

        # Establecer las nuevas posiciones de las esferas
        self.mesh.set_position(position1[:3])
        self.mesh2.set_position(position2[:3])
        
        # Rotar las esferas
        self.mesh.rotate_y(0.00514)
        self.mesh.rotate_x(0.00337)
        self.mesh2.rotate_y(-0.00514)
        self.mesh2.rotate_x(-0.00337)

        # Renderizar la escena
        self.renderer.render(self.scene, self.camera)

        # Guardar el frame actual
        width, height = 800, 600
        self.image_saver.save_frame(width, height)

# Instanciar esta clase y ejecutar el programa
Example(screen_size=[800, 600]).run()
