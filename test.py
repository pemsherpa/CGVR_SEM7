import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import sys

def draw_cube():
    # 8 corner points of a 3D cube
    vertices = (
        (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, -1),
        (1, -1, 1), (1, 1, 1), (-1, -1, 1), (-1, 1, 1)
    )
    # 12 line paths connecting those points
    edges = (
        (0,1), (0,3), (0,4), (2,1), (2,3), (2,7),
        (6,3), (6,4), (6,7), (5,1), (5,4), (5,7)
    )
    
    glBegin(GL_LINES)
    # Set the wireframe color to bright green
    glColor3f(0.0, 1.0, 0.0) 
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Local OpenGL 3D Test Cube")

    # Set up perspective camera matrix (Field of View, Aspect Ratio, Near/Far clipping)
    gluPerspective(45, (800/600), 0.1, 50.0)
    # Move the camera back 5 units along the Z axis so we can see the cube
    glTranslatef(0.0, 0.0, -5)

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Rotate the cube matrix by 1 degree around the vector axis (x=1, y=1, z=1)
        glRotatef(1, 1, 1, 1)
        
        # Clear color and depth buffers before redrawing
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        draw_cube()
        
        pygame.display.flip()
        clock.tick(60) # Limit frame rate to 60 FPS

if __name__ == "__main__":
    main()
