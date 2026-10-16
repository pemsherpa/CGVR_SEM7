
"""
LAB 10: 3D VIEWING PIPELINE
Projection and Viewport Mapping using OpenGL

Run:
    python Lab10.py

Install:
    python -m pip install PyOpenGL PyOpenGL_accelerate glfw numpy

Controls:
    SPACE - Start/stop rotation
    P     - Toggle perspective/orthographic comparison
    A     - Toggle axes
    UP    - Move camera upward
    DOWN  - Move camera downward
    LEFT  - Rotate camera left
    RIGHT - Rotate camera right
    ESC   - Exit
"""

import sys
import math
import glfw

from OpenGL.GL import *
from OpenGL.GLU import *

WIDTH = 1100
HEIGHT = 700

window = None
rotation_angle = 0.0
camera_angle = 35.0
camera_height = 2.5
animation = True
compare_views = True
show_axes = True
previous_time = 0.0


# --------------------------------------------------
# DRAW 3D AXES
# --------------------------------------------------

def draw_axes():
    glLineWidth(2.0)
    glBegin(GL_LINES)

    # X axis - red
    glColor3f(1.0, 0.2, 0.2)
    glVertex3f(-2.0, 0.0, 0.0)
    glVertex3f(2.0, 0.0, 0.0)

    # Y axis - green
    glColor3f(0.2, 1.0, 0.2)
    glVertex3f(0.0, -2.0, 0.0)
    glVertex3f(0.0, 2.0, 0.0)

    # Z axis - blue
    glColor3f(0.2, 0.5, 1.0)
    glVertex3f(0.0, 0.0, -2.0)
    glVertex3f(0.0, 0.0, 2.0)

    glEnd()


# --------------------------------------------------
# DRAW 3D CUBE
# --------------------------------------------------

def draw_cube():
    vertices = [
        (-1, -1, -1),
        ( 1, -1, -1),
        ( 1,  1, -1),
        (-1,  1, -1),
        (-1, -1,  1),
        ( 1, -1,  1),
        ( 1,  1,  1),
        (-1,  1,  1)
    ]

    faces = [
        (0, 1, 2, 3),
        (4, 5, 6, 7),
        (0, 1, 5, 4),
        (2, 3, 7, 6),
        (0, 3, 7, 4),
        (1, 2, 6, 5)
    ]

    colors = [
        (1.0, 0.25, 0.25),
        (0.2, 0.8, 0.4),
        (0.2, 0.5, 1.0),
        (1.0, 0.8, 0.2),
        (0.8, 0.3, 1.0),
        (0.2, 0.9, 0.9)
    ]

    glBegin(GL_QUADS)

    for i, face in enumerate(faces):
        glColor3f(*colors[i])

        for index in face:
            glVertex3f(*vertices[index])

    glEnd()

    # Draw cube edges
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]

    glLineWidth(2.0)
    glColor3f(0.05, 0.05, 0.05)

    glBegin(GL_LINES)

    for a, b in edges:
        glVertex3f(*vertices[a])
        glVertex3f(*vertices[b])

    glEnd()


# --------------------------------------------------
# CAMERA / VIEW TRANSFORMATION
# --------------------------------------------------

def set_camera():
    radians = math.radians(camera_angle)

    camera_x = 6.0 * math.sin(radians)
    camera_z = 6.0 * math.cos(radians)

    gluLookAt(
        camera_x, camera_height, camera_z,
        0.0, 0.0, 0.0,
        0.0, 1.0, 0.0
    )


# --------------------------------------------------
# RENDER ONE VIEWPORT
# --------------------------------------------------

def render_viewport(x, y, width, height, perspective):
    if width <= 0 or height <= 0:
        return

    # Viewport mapping: map normalized screen coordinates
    # to the specified rectangular window region.
    glViewport(x, y, width, height)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    aspect = width / float(height)

    # Projection transformation
    if perspective:
        gluPerspective(
            50.0,      # Field of view
            aspect,    # Aspect ratio
            0.1,       # Near clipping plane
            100.0      # Far clipping plane
        )
    else:
        view_size = 3.2

        glOrtho(
            -view_size * aspect,
             view_size * aspect,
            -view_size,
             view_size,
            0.1,
            100.0
        )

    # Viewing transformation
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    set_camera()

    # Model transformation
    glRotatef(rotation_angle, 0.0, 1.0, 0.0)
    glRotatef(20.0, 1.0, 0.0, 0.0)

    if show_axes:
        draw_axes()

    draw_cube()


# --------------------------------------------------
# KEYBOARD CONTROLS
# --------------------------------------------------

def keyboard_callback(win, key, scancode, action, mods):
    global animation, compare_views
    global show_axes, camera_angle, camera_height

    if action != glfw.PRESS:
        return

    if key == glfw.KEY_SPACE:
        animation = not animation

    elif key == glfw.KEY_P:
        compare_views = not compare_views

    elif key == glfw.KEY_A:
        show_axes = not show_axes

    elif key == glfw.KEY_LEFT:
        camera_angle -= 5.0

    elif key == glfw.KEY_RIGHT:
        camera_angle += 5.0

    elif key == glfw.KEY_UP:
        camera_height += 0.25

    elif key == glfw.KEY_DOWN:
        camera_height -= 0.25

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(win, True)


# --------------------------------------------------
# MAIN FUNCTION
# --------------------------------------------------

def main():
    global window, rotation_angle, previous_time

    if not glfw.init():
        print("Error: Could not initialize GLFW.")
        sys.exit(1)

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 2)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)

    window = glfw.create_window(
        WIDTH,
        HEIGHT,
        "Lab 10 - 3D Viewing Pipeline",
        None,
        None
    )

    if not window:
        glfw.terminate()
        print("Error: Could not create OpenGL window.")
        sys.exit(1)

    glfw.make_context_current(window)
    glfw.swap_interval(1)
    glfw.set_key_callback(window, keyboard_callback)

    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glClearColor(0.08, 0.09, 0.13, 1.0)

    print("\nLAB 10: 3D VIEWING PIPELINE")
    print("---------------------------")
    print("SPACE : Start/stop rotation")
    print("P     : Toggle projection comparison")
    print("A     : Toggle coordinate axes")
    print("UP/DOWN : Change camera height")
    print("LEFT/RIGHT : Rotate camera")
    print("ESC   : Exit")
    print("\nLeft viewport  : Perspective projection")
    print("Right viewport : Orthographic projection")

    previous_time = glfw.get_time()

    while not glfw.window_should_close(window):
        current_time = glfw.get_time()
        delta = current_time - previous_time
        previous_time = current_time

        if animation:
            rotation_angle = (
                rotation_angle + 45.0 * delta
            ) % 360.0

        # Retrieve actual framebuffer size.
        # This also supports high-DPI displays.
        fb_width, fb_height = glfw.get_framebuffer_size(window)

        glClear(
            GL_COLOR_BUFFER_BIT |
            GL_DEPTH_BUFFER_BIT
        )

        if compare_views:
            half_width = fb_width // 2

            # Left half: perspective projection
            render_viewport(
                0, 0,
                half_width, fb_height,
                True
            )

            # Right half: orthographic projection
            render_viewport(
                half_width, 0,
                fb_width - half_width, fb_height,
                False
            )

        else:
            # Full window: perspective projection
            render_viewport(
                0, 0,
                fb_width, fb_height,
                True
            )

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()


if __name__ == "__main__":
    main()
