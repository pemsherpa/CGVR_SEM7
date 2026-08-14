from OpenGL.GL import *
from OpenGL.GLUT import *
import math

angle = 0

def drawLine(x1, y1, x2, y2):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    sx = 1 if x2 > x1 else -1
    sy = 1 if y2 > y1 else -1

    err = dx - dy

    glBegin(GL_POINTS)

    while True:
        glVertex2i(x1, y1)

        if x1 == x2 and y1 == y2:
            break

        e2 = 2 * err

        if e2 > -dy:
            err -= dy
            x1 += sx

        if e2 < dx:
            err += dx
            y1 += sy

    glEnd()


def display():
    global angle

    glClear(GL_COLOR_BUFFER_BIT)

    radius = 250

    for i in range(72):      # 72 lines (every 5 degrees)

        theta = math.radians(i * 5 + angle)

        x = int(radius * math.cos(theta))
        y = int(radius * math.sin(theta))

        # Rainbow colours
        glColor3f(
            (math.sin(theta) + 1) / 2,
            (math.cos(theta) + 1) / 2,
            (math.sin(theta * 2) + 1) / 2,
        )

        drawLine(0, 0, x, y)

    glutSwapBuffers()


def animate():
    global angle

    angle += 1
    if angle >= 360:
        angle = 0

    glutPostRedisplay()


def init():
    glClearColor(0, 0, 0, 1)

    glPointSize(2)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-300, 300, -300, 300, -1, 1)


glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(700, 700)
glutCreateWindow(b"Bresenham Line Animation")

init()

glutDisplayFunc(display)
glutIdleFunc(animate)

glutMainLoop()