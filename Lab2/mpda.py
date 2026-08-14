import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *


# --------------------------------------------------
# Plot 8 symmetric points
# --------------------------------------------------
def plot_circle_points(xc, yc, x, y):
    points = [
        (xc + x, yc + y),
        (xc - x, yc + y),
        (xc + x, yc - y),
        (xc - x, yc - y),
        (xc + y, yc + x),
        (xc - y, yc + x),
        (xc + y, yc - x),
        (xc - y, yc - x)
    ]

    for px, py in points:
        glVertex2f(px, py)


# --------------------------------------------------
# Midpoint Circle Drawing Algorithm
# --------------------------------------------------
def midpoint_circle(xc, yc, r):

    x = 0
    y = r

    # Initial decision parameter
    p = 1 - r

    glBegin(GL_POINTS)

    while x <= y:

        # Plot 8 symmetric points
        plot_circle_points(xc, yc, x, y)

        # Update decision parameter
        if p < 0:
            p = p + 2 * x + 3
        else:
            p = p + 2 * (x - y) + 5
            y -= 1

        x += 1

    glEnd()


# --------------------------------------------------
# Draw coordinate axes
# --------------------------------------------------
def draw_axes():

    glColor3f(0.3, 0.3, 0.3)

    glBegin(GL_LINES)

    # X-axis
    glVertex2f(-500, 0)
    glVertex2f(500, 0)

    # Y-axis
    glVertex2f(0, -500)
    glVertex2f(0, 500)

    glEnd()


# --------------------------------------------------
# Main
# --------------------------------------------------

# Take input from user
xc = int(input("Enter center X (xc): "))
yc = int(input("Enter center Y (yc): "))
r = int(input("Enter radius (r): "))

if r <= 0:
    print("Radius must be greater than 0.")
    exit()


# Window size
WIDTH = 800
HEIGHT = 800

pygame.init()

pygame.display.set_caption("Midpoint Circle Drawing Algorithm")

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT),
    DOUBLEBUF | OPENGL
)


# --------------------------------------------------
# OpenGL setup
# --------------------------------------------------

glClearColor(0.0, 0.0, 0.0, 1.0)

# Coordinate system
glMatrixMode(GL_PROJECTION)
glLoadIdentity()

gluOrtho2D(
    -WIDTH // 2,
    WIDTH // 2,
    -HEIGHT // 2,
    HEIGHT // 2
)

glMatrixMode(GL_MODELVIEW)
glLoadIdentity()


# Make points visible
glPointSize(3)


# --------------------------------------------------
# Main loop
# --------------------------------------------------

running = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # Press ESC to exit
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False


    # Clear screen
    glClear(GL_COLOR_BUFFER_BIT)

    # Draw coordinate axes
    draw_axes()

    # Draw circle
    glColor3f(1.0, 1.0, 1.0)

    midpoint_circle(xc, yc, r)

    # Mark center
    glPointSize(7)

    glColor3f(1.0, 0.0, 0.0)

    glBegin(GL_POINTS)
    glVertex2f(xc, yc)
    glEnd()

    glPointSize(3)

    pygame.display.flip()


pygame.quit()