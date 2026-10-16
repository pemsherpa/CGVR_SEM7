
"""
EXPERIMENT 10
2D Geometric Transformations and 3D Viewing Pipeline

Run:
    python Lab8.py

Install dependencies:
    python -m pip install PyOpenGL PyOpenGL_accelerate glfw numpy

Controls:
    1 - Translation
    2 - Rotation
    3 - Scaling
    4 - Reflection about X-axis
    5 - Shearing
    6 - Rotation about arbitrary pivot
    7 - Non-uniform scaling
    8 - Reflection about y = x
    9 - Composite transformation
    0 - Continuous rotation
    V - Toggle 3D viewing pipeline
    M - Display menu in terminal
    ESC - Exit
"""

import math
import sys

import glfw
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *


WIDTH = 1000
HEIGHT = 700

window = None
mode = "original"
show_3d = False
animate = False
angle = 0.0
last_time = 0.0

# Polygon vertices in homogeneous coordinates (x, y, 1).
BASE_POINTS = np.array([
    [-0.55, -0.35, 1.0],
    [ 0.00, -0.35, 1.0],
    [ 0.00, -0.55, 1.0],
    [ 0.55,  0.00, 1.0],
    [ 0.00,  0.55, 1.0],
    [ 0.00,  0.35, 1.0],
    [-0.55,  0.35, 1.0],
], dtype=float)

PIVOT = (0.25, 0.15)


# ---------------------------------------------------------
# 2D HOMOGENEOUS TRANSFORMATION MATRICES
# ---------------------------------------------------------

def translation(tx, ty):
    """Translation matrix."""
    return np.array([
        [1, 0, tx],
        [0, 1, ty],
        [0, 0, 1]
    ], dtype=float)


def rotation(degrees):
    """Rotation about the origin."""
    theta = math.radians(degrees)
    c = math.cos(theta)
    s = math.sin(theta)

    return np.array([
        [c, -s, 0],
        [s,  c, 0],
        [0,  0, 1]
    ], dtype=float)


def scaling(sx, sy):
    """Scaling matrix."""
    return np.array([
        [sx, 0,  0],
        [0,  sy, 0],
        [0,  0,  1]
    ], dtype=float)


def reflection_x_axis():
    """Reflection about the X-axis."""
    return scaling(1, -1)


def reflection_y_axis():
    """Reflection about the Y-axis."""
    return scaling(-1, 1)


def reflection_y_eq_x():
    """Reflection about the line y = x."""
    return np.array([
        [0, 1, 0],
        [1, 0, 0],
        [0, 0, 1]
    ], dtype=float)


def shearing(shx, shy):
    """Shearing matrix."""
    return np.array([
        [1,   shx, 0],
        [shy, 1,   0],
        [0,   0,   1]
    ], dtype=float)


def about_pivot(matrix, px, py):
    """
    Apply a transformation about arbitrary pivot (px, py).

    First translate the pivot to the origin,
    apply the transformation, then translate it back.
    """
    return (
        translation(px, py)
        @ matrix
        @ translation(-px, -py)
    )


def transform_points(points, matrix):
    """Apply one 3x3 matrix to all polygon vertices."""
    return (matrix @ points.T).T


# ---------------------------------------------------------
# SELECT TRANSFORMATION
# ---------------------------------------------------------

def current_matrix():
    if mode == "translation":
        return translation(0.35, 0.20)

    elif mode == "rotation":
        return rotation(35)

    elif mode == "scaling":
        return scaling(1.35, 0.70)

    elif mode == "reflection":
        return reflection_x_axis()

    elif mode == "shearing":
        return shearing(0.65, 0.0)

    elif mode == "pivot":
        return about_pivot(rotation(50), *PIVOT)

    elif mode == "nonuniform":
        return scaling(1.45, 0.60)

    elif mode == "y_equals_x":
        return reflection_y_eq_x()

    elif mode == "composite":
        # Applied to points from right to left:
        # scaling -> rotation -> translation.
        return (
            translation(0.20, 0.12)
            @ rotation(25)
            @ scaling(1.15, 0.80)
        )

    elif mode == "animation":
        return rotation(angle)

    return np.eye(3)


# ---------------------------------------------------------
# 2D OPENGL DISPLAY
# ---------------------------------------------------------

def draw_polygon(points, color, filled=True):
    """Draw a polygon using OpenGL."""
    glColor3f(*color)

    if filled:
        glBegin(GL_POLYGON)
    else:
        glBegin(GL_LINE_LOOP)

    for x, y, _ in points:
        glVertex2f(float(x), float(y))

    glEnd()


def draw_axes():
    """Draw coordinate axes and the y=x reference line."""
    glLineWidth(1.0)
    glColor3f(0.35, 0.37, 0.42)

    glBegin(GL_LINES)

    # X-axis
    glVertex2f(-0.95, 0)
    glVertex2f(0.95, 0)

    # Y-axis
    glVertex2f(0, -0.88)
    glVertex2f(0, 0.88)

    glEnd()

    if mode == "y_equals_x":
        glColor3f(1.0, 0.70, 0.15)

        glBegin(GL_LINES)
        glVertex2f(-0.85, -0.85)
        glVertex2f(0.85, 0.85)
        glEnd()


def draw_2d():
    """Display original and transformed polygons."""
    glViewport(0, 0, WIDTH, HEIGHT)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-1.0, 1.0, -0.9, 0.9, -1.0, 1.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    draw_axes()

    # Original polygon: gray outline.
    draw_polygon(
        BASE_POINTS,
        (0.45, 0.48, 0.54),
        filled=False
    )

    # Transform all vertices using matrix multiplication.
    matrix = current_matrix()
    transformed = transform_points(BASE_POINTS, matrix)

    # Transformed polygon: blue fill and light outline.
    draw_polygon(
        transformed,
        (0.12, 0.55, 0.85),
        filled=True
    )

    draw_polygon(
        transformed,
        (0.85, 0.95, 1.0),
        filled=False
    )

    # Mark the arbitrary rotation pivot.
    if mode == "pivot":
        px, py = PIVOT

        glPointSize(10)
        glColor3f(1.0, 0.15, 0.15)

        glBegin(GL_POINTS)
        glVertex2f(px, py)
        glEnd()


# ---------------------------------------------------------
# 3D VIEWING PIPELINE
# ---------------------------------------------------------

def draw_3d_pipeline():
    """
    Demonstrate:
    1. 3D model coordinates
    2. Viewing transformation
    3. Perspective projection
    4. Viewport mapping
    """
    glViewport(0, 0, WIDTH, HEIGHT)
    glEnable(GL_DEPTH_TEST)

    # Perspective projection matrix.
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    gluPerspective(
        45.0,
        WIDTH / float(HEIGHT),
        0.1,
        100.0
    )

    # Camera/view transformation.
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    gluLookAt(
        3.2, 2.4, 5.0,  # Camera position
        0.0, 0.0, 0.0,  # Look-at point
        0.0, 1.0, 0.0   # Up direction
    )

    # Rotate the cube.
    glRotatef(
        angle if animate else 25.0,
        0.3, 1.0, 0.0
    )

    # Six colored faces of a cube.
    faces = [
        ((1.0, 0.2, 0.2), [
            (-1, -1, 1), (1, -1, 1),
            (1, 1, 1), (-1, 1, 1)
        ]),
        ((0.2, 0.8, 0.3), [
            (-1, -1, -1), (-1, 1, -1),
            (1, 1, -1), (1, -1, -1)
        ]),
        ((0.2, 0.4, 1.0), [
            (1, -1, -1), (1, 1, -1),
            (1, 1, 1), (1, -1, 1)
        ]),
        ((1.0, 0.8, 0.2), [
            (-1, -1, -1), (-1, -1, 1),
            (-1, 1, 1), (-1, 1, -1)
        ]),
        ((0.8, 0.3, 0.9), [
            (-1, 1, -1), (-1, 1, 1),
            (1, 1, 1), (1, 1, -1)
        ]),
        ((0.2, 0.8, 0.9), [
            (-1, -1, -1), (1, -1, -1),
            (1, -1, 1), (-1, -1, 1)
        ])
    ]

    glBegin(GL_QUADS)

    for color, vertices in faces:
        glColor3f(*color)

        for vertex in vertices:
            glVertex3f(*vertex)

    glEnd()

    glDisable(GL_DEPTH_TEST)


# ---------------------------------------------------------
# MENU
# ---------------------------------------------------------

def print_menu():
    print("\n" + "=" * 60)
    print("EXPERIMENT 10: COMPUTER GRAPHICS")
    print("2D TRANSFORMATIONS AND 3D VIEWING PIPELINE")
    print("=" * 60)

    print("1. Translation")
    print("2. Rotation about origin")
    print("3. Scaling")
    print("4. Reflection about X-axis")
    print("5. Shearing")
    print("6. Rotation about arbitrary pivot")
    print("7. Non-uniform scaling")
    print("8. Reflection about y = x")
    print("9. Composite transformation")
    print("0. Toggle continuous rotation")
    print("V. Toggle 3D viewing pipeline")
    print("M. Display menu")
    print("ESC. Exit")

    print("\nGray outline = original polygon")
    print("Blue polygon = transformed polygon")
    print("=" * 60)


# ---------------------------------------------------------
# KEYBOARD INPUT
# ---------------------------------------------------------

def key_callback(win, key, scancode, action, mods):
    global mode, show_3d, animate

    if action not in (glfw.PRESS, glfw.REPEAT):
        return

    transformations = {
        glfw.KEY_1: "translation",
        glfw.KEY_2: "rotation",
        glfw.KEY_3: "scaling",
        glfw.KEY_4: "reflection",
        glfw.KEY_5: "shearing",
        glfw.KEY_6: "pivot",
        glfw.KEY_7: "nonuniform",
        glfw.KEY_8: "y_equals_x",
        glfw.KEY_9: "composite"
    }

    if key in transformations:
        mode = transformations[key]
        show_3d = False
        print("Selected transformation:", mode)

    elif key == glfw.KEY_0:
        animate = not animate
        mode = "animation"
        show_3d = False

        print(
            "Continuous rotation:",
            "ON" if animate else "OFF"
        )

    elif key == glfw.KEY_V:
        show_3d = not show_3d
        print(
            "3D viewing pipeline:",
            "ON" if show_3d else "OFF"
        )

    elif key == glfw.KEY_M:
        print_menu()

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(win, True)


# ---------------------------------------------------------
# MAIN PROGRAM
# ---------------------------------------------------------

def main():
    global window, angle, last_time

    if not glfw.init():
        print("ERROR: GLFW initialization failed.")
        sys.exit(1)

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 2)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)

    window = glfw.create_window(
        WIDTH,
        HEIGHT,
        "Experiment 10 - Graphics Transformations",
        None,
        None
    )

    if not window:
        glfw.terminate()
        print("ERROR: Could not create OpenGL window.")
        sys.exit(1)

    glfw.make_context_current(window)
    glfw.swap_interval(1)

    glfw.set_key_callback(window, key_callback)

    glClearColor(0.07, 0.08, 0.11, 1.0)

    print_menu()
    last_time = glfw.get_time()

    while not glfw.window_should_close(window):
        now = glfw.get_time()
        delta_time = now - last_time
        last_time = now

        # Continuous rotation animation.
        if animate:
            angle = (angle + 70.0 * delta_time) % 360.0

        glClear(
            GL_COLOR_BUFFER_BIT |
            GL_DEPTH_BUFFER_BIT
        )

        if show_3d:
            draw_3d_pipeline()
        else:
            glDisable(GL_DEPTH_TEST)
            draw_2d()

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()


if __name__ == "__main__":
    main()
