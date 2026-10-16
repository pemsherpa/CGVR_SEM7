"""
===============================================================================
EXPERIMENT - 6: IMPLEMENT THE Z-BUFFER ALGORITHM FOR HIDDEN SURFACE REMOVAL
===============================================================================
Course Outcome: CO3 - Apply 3D graphics concepts and visible surface detection 
                algorithms (Z-Buffer / Depth Buffer) for realistic object rendering.
Bloom's Taxonomy Level: L3 - Apply

Aim:
To implement the Z-Buffer (Depth-Buffer) algorithm for hidden surface removal
in OpenGL, demonstrating depth comparison, surface visibility determination,
and resolving overlapping and intersecting 3D surfaces.

Theoretical Background:
The Z-Buffer (or Depth-Buffer) algorithm is a fundamental image-space method
for hidden surface detection. It uses two 2D buffer arrays:
1. Frame Buffer (Color Buffer): Stores color values for each pixel (x, y).
2. Depth Buffer (Z-Buffer): Stores the depth / closest z-value for each pixel (x, y).

Mathematical Formula:
Plane Equation: A*x + B*y + C*z + D = 0
At pixel (x, y):
    z = (-A*x - B*y - D) / C
Along a scan line (incremental depth calculation):
    z(x + 1, y) = z(x, y) - (A / C)

Algorithm Steps:
1. Initialize depth_buffer[x, y] = 1.0 (maximum depth / far plane).
2. Initialize frame_buffer[x, y] = background_color.
3. For each polygon in the scene:
    For each pixel (x, y) covered by the projected polygon:
        Calculate depth z(x, y).
        If z(x, y) < depth_buffer[x, y]:
            depth_buffer[x, y] = z(x, y)
            frame_buffer[x, y] = polygon_color
4. Display the resulting frame_buffer.
===============================================================================
"""

import sys
import math
import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *


# ============================================================
# GLOBAL CONFIGURATION & STATE
# ============================================================

window_width = 1000
window_height = 700

# Z-Buffer state
z_buffer_enabled = True
depth_view_mode = False       # True: visualize depth map in grayscale
reverse_draw_order = False    # True: render polygons back-to-front or front-to-back
auto_rotate = False
show_hud = True

# Scene selection
current_scene = 1             # 1: Overlapping Polygons, 2: Intersecting Surfaces, 3: 3D Solid Objects, 4: Discrete Pixel Grid Simulation

# 3D Camera / Rotation variables
rot_x = 20.0
rot_y = -30.0
zoom_distance = -7.0

# Mouse interaction variables
last_mouse_x = 0
last_mouse_y = 0
mouse_dragging = False


# ============================================================
# COLOR PALETTE (VIBRANT & DISTINCT FOR ACADEMIC CLARITY)
# ============================================================

COLOR_RED    = (0.92, 0.26, 0.21)
COLOR_GREEN  = (0.18, 0.80, 0.44)
COLOR_BLUE   = (0.20, 0.60, 1.00)
COLOR_YELLOW = (0.98, 0.77, 0.19)
COLOR_PURPLE = (0.61, 0.35, 0.71)
COLOR_CYAN   = (0.16, 0.83, 0.83)
COLOR_ORANGE = (0.95, 0.51, 0.13)
COLOR_WHITE  = (1.00, 1.00, 1.00)
COLOR_GRAY   = (0.45, 0.45, 0.45)
COLOR_DARK   = (0.10, 0.12, 0.16)


# ============================================================
# HUD TEXT RENDERING UTILITIES
# ============================================================

def draw_text_2d(x, y, text, color=(1.0, 1.0, 1.0), font=GLUT_BITMAP_HELVETICA_12):
    """Render 2D bitmap text overlay using screen pixel coordinates."""
    glColor3f(color[0], color[1], color[2])
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))


def render_hud():
    """Renders on-screen HUD with status, controls, and theoretical context."""
    if not show_hud:
        return

    # Switch to 2D Orthographic Projection for HUD overlay
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Disable depth testing while rendering 2D HUD text
    glDisable(GL_DEPTH_TEST)

    # Semi-transparent background panel for header
    glColor4f(0.06, 0.08, 0.12, 0.85)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glBegin(GL_QUADS)
    glVertex2f(10, window_height - 10)
    glVertex2f(window_width - 10, window_height - 10)
    glVertex2f(window_width - 10, window_height - 85)
    glVertex2f(10, window_height - 85)
    glEnd()

    # Header Text
    draw_text_2d(25, window_height - 35, 
                 "EXPERIMENT 6: Z-BUFFER ALGORITHM FOR HIDDEN SURFACE REMOVAL", 
                 COLOR_YELLOW, GLUT_BITMAP_HELVETICA_18)
    draw_text_2d(25, window_height - 58, 
                 "Course: CGVR (Sem 7) | CO3: Depth-Buffer & Visible Surface Detection | Bloom: L3-Apply", 
                 (0.8, 0.8, 0.8), GLUT_BITMAP_HELVETICA_12)
    draw_text_2d(25, window_height - 75, 
                 "Formula: Ax + By + Cz + D = 0  ==>  z = (-Ax - By - D)/C  |  Delta z = -A/C per scanline step", 
                 (0.6, 0.9, 1.0), GLUT_BITMAP_HELVETICA_10)

    # Bottom Info Panel
    panel_height = 125
    glColor4f(0.06, 0.08, 0.12, 0.85)
    glBegin(GL_QUADS)
    glVertex2f(10, 10 + panel_height)
    glVertex2f(window_width - 10, 10 + panel_height)
    glVertex2f(window_width - 10, 10)
    glVertex2f(10, 10)
    glEnd()
    glDisable(GL_BLEND)

    # Status Indicators
    status_z = "ENABLED [Correct Hidden Surface Removal]" if z_buffer_enabled else "DISABLED [Overwriting / Depth Failure!]"
    color_z = COLOR_GREEN if z_buffer_enabled else COLOR_RED
    draw_text_2d(25, 108, f"Z-Buffer (Depth Test): {status_z}", color_z, GLUT_BITMAP_HELVETICA_12)

    scene_names = [
        "1. Overlapping Polygons (Depth Complexity & Ordering)",
        "2. Intersecting Surfaces (Painter's Algorithm Failure Demo)",
        "3. 3D Rotating Solid Objects (Cube / Polyhedra)",
        "4. Discrete Software Z-Buffer Simulation (Pixel & Depth Grid)"
    ]
    draw_text_2d(25, 88, f"Current Scene: {scene_names[current_scene - 1]}", COLOR_CYAN, GLUT_BITMAP_HELVETICA_12)

    order_str = "Reversed (Front-to-Back)" if reverse_draw_order else "Standard (Back-to-Front)"
    draw_text_2d(25, 68, f"Draw Submission Order: {order_str} | View Mode: {'Grayscale Depth Map' if depth_view_mode else 'RGB Color'}", 
                 (0.85, 0.85, 0.85), GLUT_BITMAP_HELVETICA_10)

    # Key Controls Guide
    draw_text_2d(25, 45, "[Z] Toggle Z-Buffer  |  [1-4] Select Scene  |  [O] Toggle Draw Order  |  [D] Depth Map View  |  [Space] Auto-Rotate", 
                 COLOR_YELLOW, GLUT_BITMAP_HELVETICA_10)
    draw_text_2d(25, 25, "[Mouse Drag / Arrows] Rotate 3D  |  [+/-] Zoom  |  [R] Reset Camera  |  [H] Toggle HUD Overlay", 
                 (0.7, 0.7, 0.7), GLUT_BITMAP_HELVETICA_10)

    # Restore 3D Modelview / Projection state
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    # Re-enable depth testing if active
    if z_buffer_enabled:
        glEnable(GL_DEPTH_TEST)


# ============================================================
# SCENE 1: OVERLAPPING POLYGONS AT DIFFERENT DEPTHS
# ============================================================

def draw_scene_1_overlapping_polygons():
    """
    Renders 3 overlapping polygons positioned at distinct Z depths:
      - Polygon A (Red): Closest to camera (Z = -2.0)
      - Polygon B (Green): Middle depth (Z = -3.5)
      - Polygon C (Blue): Farthest back (Z = -5.0)

    Demonstrates:
    - With Z-Buffer ON: Red is always in front, Green in middle, Blue behind,
      REGARDLESS of draw submission order.
    - With Z-Buffer OFF: Whichever polygon is drawn last completely paints over
      earlier ones, violating 3D depth reality.
    """
    polygons = [
        # (name, color, z_depth, vertices)
        ("Polygon C (Farthest, Z=-5.0)", COLOR_BLUE, -5.0, [
            (-2.5, -1.8), (1.5, -1.8), (1.5, 2.2), (-2.5, 2.2)
        ]),
        ("Polygon B (Middle, Z=-3.5)", COLOR_GREEN, -3.5, [
            (-1.2, -2.5), (2.8, -2.5), (2.8, 1.5), (-1.2, 1.5)
        ]),
        ("Polygon A (Closest, Z=-2.0)", COLOR_RED, -2.0, [
            (-0.2, -1.2), (3.8, -1.2), (3.8, 2.8), (-0.2, 2.8)
        ])
    ]

    # Invert drawing order if requested to show painter's algorithm discrepancy
    order = list(reversed(polygons)) if reverse_draw_order else polygons

    for name, col, z, verts in order:
        if depth_view_mode:
            # Map depth [-5.0, -2.0] to grayscale intensity [0.2, 0.9]
            intensity = 0.2 + (z - (-5.0)) / 3.0 * 0.7
            glColor3f(intensity, intensity, intensity)
        else:
            glColor3f(*col)

        glBegin(GL_POLYGON)
        for vx, vy in verts:
            glVertex3f(vx, vy, z)
        glEnd()

        # Black outline for crisp geometric definition
        glColor3f(0.1, 0.1, 0.1)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        for vx, vy in verts:
            glVertex3f(vx, vy, z + 0.005) # Tiny bias to prevent z-fighting on line
        glEnd()


# ============================================================
# SCENE 2: INTERSECTING SURFACES (PAINTER'S ALGORITHM FAILURE)
# ============================================================

def draw_scene_2_intersecting_surfaces():
    """
    Renders two intersecting 3D planes:
      - Plane 1 (Red / Orange): Passes through (0, 0, 0) inclined along X-Z.
      - Plane 2 (Blue / Cyan): Passes through (0, 0, 0) inclined along Y-Z.

    Significance:
    Painter's Algorithm FAILS on intersecting surfaces without splitting geometry
    because neither plane is strictly entirely in front of the other.
    The Z-Buffer solves this per-pixel effortlessly without geometric partitioning.
    """
    surfaces = [
        # (Color, vertices with explicit 3D (x, y, z))
        (COLOR_RED, [
            (-2.5, 0.0, -2.5),
            ( 2.5, 0.0,  2.5),
            ( 2.5, 2.5,  2.5),
            (-2.5, 2.5, -2.5)
        ]),
        (COLOR_BLUE, [
            (0.0, -2.5, -2.5),
            (0.0,  2.5,  2.5),
            (2.5,  2.5,  2.5),
            (2.5, -2.5, -2.5)
        ]),
        (COLOR_YELLOW, [
            (-2.0, -2.0,  1.5),
            ( 2.0, -2.0, -1.5),
            ( 2.0,  1.0, -1.5),
            (-2.0,  1.0,  1.5)
        ])
    ]

    order = list(reversed(surfaces)) if reverse_draw_order else surfaces

    for col, verts in order:
        if depth_view_mode:
            # Grayscale based on average Z
            avg_z = sum(v[2] for v in verts) / len(verts)
            intensity = 0.5 + (avg_z / 6.0)
            glColor3f(intensity, intensity, intensity)
        else:
            glColor3f(*col)

        glBegin(GL_POLYGON)
        for vx, vy, vz in verts:
            glVertex3f(vx, vy, vz)
        glEnd()

        # Outline
        glColor3f(0.05, 0.05, 0.05)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        for vx, vy, vz in verts:
            glVertex3f(vx, vy, vz)
        glEnd()


# ============================================================
# SCENE 3: 3D ROTATING SOLID OBJECTS (CUBE & PYRAMID)
# ============================================================

def draw_scene_3_solid_objects():
    """
    Renders solid 3D polyhedra (Cube and Pyramid) with distinct colored faces.
    Demonstrates hidden surface removal for closed volumes:
    - With Z-Buffer ON: Front-facing polygons hide rear-facing polygons.
    - With Z-Buffer OFF: Back faces bleed through and overwrite front faces
      during rotation.
    """
    # 1. Cube centered at (-1.8, 0, 0)
    glPushMatrix()
    glTranslatef(-1.8, 0.0, 0.0)
    glScalef(1.2, 1.2, 1.2)

    faces = [
        # (Color, [vertices])
        (COLOR_RED,    [(-1, -1,  1), ( 1, -1,  1), ( 1,  1,  1), (-1,  1,  1)]), # Front
        (COLOR_BLUE,   [(-1, -1, -1), (-1,  1, -1), ( 1,  1, -1), ( 1, -1, -1)]), # Back
        (COLOR_GREEN,  [(-1,  1, -1), (-1,  1,  1), ( 1,  1,  1), ( 1,  1, -1)]), # Top
        (COLOR_YELLOW, [(-1, -1, -1), ( 1, -1, -1), ( 1, -1,  1), (-1, -1,  1)]), # Bottom
        (COLOR_PURPLE, [( 1, -1, -1), ( 1,  1, -1), ( 1,  1,  1), ( 1, -1,  1)]), # Right
        (COLOR_CYAN,   [(-1, -1, -1), (-1, -1,  1), (-1,  1,  1), (-1,  1, -1)])  # Left
    ]

    order = list(reversed(faces)) if reverse_draw_order else faces

    for col, verts in order:
        if depth_view_mode:
            glColor3f(0.7, 0.7, 0.7)
        else:
            glColor3f(*col)

        glBegin(GL_QUADS)
        for vx, vy, vz in verts:
            glVertex3f(vx, vy, vz)
        glEnd()

        # Wireframe border
        glColor3f(0.1, 0.1, 0.1)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        for vx, vy, vz in verts:
            glVertex3f(vx, vy, vz)
        glEnd()

    glPopMatrix()

    # 2. Pyramid centered at (1.8, 0, 0)
    glPushMatrix()
    glTranslatef(1.8, -0.5, 0.0)
    glScalef(1.4, 1.4, 1.4)

    apex = (0.0, 1.8, 0.0)
    b1 = (-1.0, 0.0,  1.0)
    b2 = ( 1.0, 0.0,  1.0)
    b3 = ( 1.0, 0.0, -1.0)
    b4 = (-1.0, 0.0, -1.0)

    pyramid_faces = [
        (COLOR_ORANGE, [apex, b1, b2]),
        (COLOR_GREEN,  [apex, b2, b3]),
        (COLOR_PURPLE, [apex, b3, b4]),
        (COLOR_CYAN,   [apex, b4, b1]),
        (COLOR_YELLOW, [b1, b4, b3, b2]) # Base
    ]

    p_order = list(reversed(pyramid_faces)) if reverse_draw_order else pyramid_faces

    for col, verts in p_order:
        glColor3f(*col)
        glBegin(GL_POLYGON)
        for v in verts:
            glVertex3f(*v)
        glEnd()

        glColor3f(0.1, 0.1, 0.1)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        for v in verts:
            glVertex3f(*v)
        glEnd()

    glPopMatrix()


# ============================================================
# SCENE 4: DISCRETE SOFTWARE Z-BUFFER SIMULATION
# ============================================================

def draw_scene_4_discrete_simulation():
    """
    Renders an on-screen simulation of the Discrete Z-Buffer Algorithm
    at the pixel grid level:
    - Demonstrates two overlapping 2D projected polygons:
        Polygon 1 (Blue): depth z = 0.70
        Polygon 2 (Red):  depth z = 0.35 (closer!)
    - Left side: Frame Buffer (Color assigned to each cell)
    - Right side: Depth Buffer (Numerical z-values stored per cell)
    """
    # Switch to 2D view for clear pixel matrix visualization
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)

    grid_size = 10
    cell_w = 32
    cell_h = 32

    # Left Grid: Frame Buffer (Color)
    start_x1 = 90
    start_y1 = 200

    # Right Grid: Depth Buffer (Z-Values)
    start_x2 = 540
    start_y2 = 200

    draw_text_2d(start_x1, start_y1 + grid_size * cell_h + 30, 
                 "FRAME BUFFER (Pixel Colors)", COLOR_CYAN, GLUT_BITMAP_HELVETICA_18)
    draw_text_2d(start_x2, start_y2 + grid_size * cell_h + 30, 
                 "Z-BUFFER (Stored Depth Values)", COLOR_YELLOW, GLUT_BITMAP_HELVETICA_18)

    draw_text_2d(start_x1, start_y1 + grid_size * cell_h + 10,
                 "Polygon 1: Blue (Depth z = 0.70)  |  Polygon 2: Red (Depth z = 0.35, CLOSER)", 
                 (0.9, 0.9, 0.9), GLUT_BITMAP_HELVETICA_12)
    draw_text_2d(start_x2, start_y2 + grid_size * cell_h + 10,
                 "Test: If (z_new < depth_buffer[x,y]) => depth_buffer = z_new, color = new_color",
                 (0.7, 1.0, 0.7), GLUT_BITMAP_HELVETICA_12)

    # Calculate discrete depth and color buffers for 10x10 grid
    # Initialized to depth = 1.00 (infinity) and background color dark gray
    depth_grid = np.full((grid_size, grid_size), 1.00, dtype=float)
    color_grid = [[(0.18, 0.20, 0.24) for _ in range(grid_size)] for _ in range(grid_size)]

    # Rasterize Polygon 1 (Blue, z=0.70, covers row 2..7, col 1..6)
    for r in range(2, 8):
        for c in range(1, 7):
            z_poly1 = 0.70
            if z_poly1 < depth_grid[r, c]:
                depth_grid[r, c] = z_poly1
                color_grid[r][c] = COLOR_BLUE

    # Rasterize Polygon 2 (Red, z=0.35, covers row 4..9, col 3..8)
    # At overlap cells (r: 4..7, c: 3..6), z=0.35 < 0.70 => Replaces blue with red!
    for r in range(4, 10):
        for c in range(3, 9):
            z_poly2 = 0.35
            # If Z-Buffer is enabled, do depth test; if disabled, overwrite blindly
            if (not z_buffer_enabled) or (z_poly2 < depth_grid[r, c]):
                depth_grid[r, c] = z_poly2
                color_grid[r][c] = COLOR_RED

    # Render Left Grid (Color Frame Buffer)
    for r in range(grid_size):
        for c in range(grid_size):
            cx = start_x1 + c * cell_w
            cy = start_y1 + r * cell_h
            col = color_grid[r][c]

            glColor3f(*col)
            glBegin(GL_QUADS)
            glVertex2f(cx, cy)
            glVertex2f(cx + cell_w - 2, cy)
            glVertex2f(cx + cell_w - 2, cy + cell_h - 2)
            glVertex2f(cx, cy + cell_h - 2)
            glEnd()

            # Cell coordinates
            draw_text_2d(cx + 4, cy + 10, f"{c},{r}", (0.1, 0.1, 0.1), GLUT_BITMAP_HELVETICA_10)

    # Render Right Grid (Depth Buffer Values)
    for r in range(grid_size):
        for c in range(grid_size):
            cx = start_x2 + c * cell_w
            cy = start_y2 + r * cell_h
            z_val = depth_grid[r, c]

            # Background color gradient according to depth
            intensity = 0.15 + (1.0 - z_val) * 0.75
            glColor3f(intensity * 0.3, intensity * 0.7, intensity)
            glBegin(GL_QUADS)
            glVertex2f(cx, cy)
            glVertex2f(cx + cell_w - 2, cy)
            glVertex2f(cx + cell_w - 2, cy + cell_h - 2)
            glVertex2f(cx, cy + cell_h - 2)
            glEnd()

            # Text showing exact stored Z-value
            text_z = "INF" if z_val >= 1.0 else f"{z_val:.2f}"
            t_col = (1.0, 1.0, 1.0) if z_val < 1.0 else (0.5, 0.5, 0.5)
            draw_text_2d(cx + 3, cy + 11, text_z, t_col, GLUT_BITMAP_HELVETICA_10)

    # Restore matrix state
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    if z_buffer_enabled:
        glEnable(GL_DEPTH_TEST)


# ============================================================
# MAIN DISPLAY FUNCTION
# ============================================================

def display():
    """Main rendering callback for GLUT display."""
    # Set background color
    glClearColor(0.08, 0.10, 0.14, 1.0)

    # Clear both Color Buffer and Depth Buffer (Z-Buffer)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Configure OpenGL Depth Testing state
    if z_buffer_enabled:
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS) # Pass if incoming depth is strictly closer than stored depth
    else:
        glDisable(GL_DEPTH_TEST) # Disable depth testing to demonstrate painter's anomaly

    # Setup 3D camera projection and transformation
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Apply 3D Camera transformations for Scenes 1, 2, 3
    if current_scene != 4:
        glTranslatef(0.0, 0.0, zoom_distance)
        glRotatef(rot_x, 1.0, 0.0, 0.0)
        glRotatef(rot_y, 0.0, 1.0, 0.0)

        # Draw subtle reference 3D ground grid for spatial orientation
        draw_ground_grid()

        # Render the selected scene
        if current_scene == 1:
            draw_scene_1_overlapping_polygons()
        elif current_scene == 2:
            draw_scene_2_intersecting_surfaces()
        elif current_scene == 3:
            draw_scene_3_solid_objects()
    else:
        # Scene 4: Discrete 2D software simulation
        draw_scene_4_discrete_simulation()

    # Draw on-screen HUD text
    render_hud()

    glutSwapBuffers()


def draw_ground_grid():
    """Draws a subtle 3D reference grid."""
    glDisable(GL_DEPTH_TEST) if not z_buffer_enabled else None
    glColor4f(0.2, 0.25, 0.32, 0.4)
    glLineWidth(1.0)
    glBegin(GL_LINES)
    grid_span = 5
    for i in range(-grid_span, grid_span + 1):
        glVertex3f(float(i), -2.6, -float(grid_span))
        glVertex3f(float(i), -2.6, float(grid_span))
        glVertex3f(-float(grid_span), -2.6, float(i))
        glVertex3f(float(grid_span), -2.6, float(i))
    glEnd()


# ============================================================
# ANIMATION & INTERACTION HANDLERS
# ============================================================

def idle():
    """Continuous idle callback for auto-rotation."""
    global rot_y
    if auto_rotate and current_scene != 4:
        rot_y = (rot_y + 0.6) % 360.0
        glutPostRedisplay()


def keyboard(key, x, y):
    """Handles keyboard shortcuts."""
    global z_buffer_enabled, current_scene, reverse_draw_order
    global depth_view_mode, auto_rotate, show_hud, rot_x, rot_y, zoom_distance

    ch = key.decode("utf-8") if isinstance(key, bytes) else key

    if ch in ('z', 'Z'):
        z_buffer_enabled = not z_buffer_enabled
        status = "ENABLED (Visible Surface Removal Active)" if z_buffer_enabled else "DISABLED (Surface Overwriting / Depth Artifacts Active)"
        print(f"\n[EVENT] Z-Buffer Depth Test: {status}")

    elif ch in ('1', '2', '3', '4'):
        current_scene = int(ch)
        print(f"\n[EVENT] Switched to Scene {current_scene}")

    elif ch in ('o', 'O'):
        reverse_draw_order = not reverse_draw_order
        print(f"\n[EVENT] Polygon Submission Order: {'Reversed' if reverse_draw_order else 'Standard'}")

    elif ch in ('d', 'D'):
        depth_view_mode = not depth_view_mode
        print(f"\n[EVENT] Depth Map Visualizer: {'ON (Grayscale)' if depth_view_mode else 'OFF (Color)'}")

    elif ch == ' ':
        auto_rotate = not auto_rotate
        print(f"\n[EVENT] Auto-Rotation: {'ON' if auto_rotate else 'OFF'}")

    elif ch in ('h', 'H'):
        show_hud = not show_hud

    elif ch in ('r', 'R'):
        rot_x = 20.0
        rot_y = -30.0
        zoom_distance = -7.0
        print("\n[EVENT] View Reset to Default")

    elif ch in ('+', '='):
        zoom_distance += 0.5
    elif ch in ('-', '_'):
        zoom_distance -= 0.5

    elif ch in ('\x1b', 'q', 'Q'): # ESC or Q to quit
        print("\n[INFO] Exiting Program. Thank you!")
        sys.exit(0)

    glutPostRedisplay()


def special_keys(key, x, y):
    """Handles arrow keys for smooth 3D scene rotation."""
    global rot_x, rot_y
    step = 5.0

    if key == GLUT_KEY_UP:
        rot_x -= step
    elif key == GLUT_KEY_DOWN:
        rot_x += step
    elif key == GLUT_KEY_LEFT:
        rot_y -= step
    elif key == GLUT_KEY_RIGHT:
        rot_y += step

    glutPostRedisplay()


def mouse(button, state, x, y):
    """Handles mouse click events for interactive rotation."""
    global mouse_dragging, last_mouse_x, last_mouse_y

    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            mouse_dragging = True
            last_mouse_x = x
            last_mouse_y = y
        elif state == GLUT_UP:
            mouse_dragging = False


def mouse_motion(x, y):
    """Handles mouse drag for continuous 3D rotation."""
    global rot_x, rot_y, last_mouse_x, last_mouse_y

    if mouse_dragging:
        dx = x - last_mouse_x
        dy = y - last_mouse_y
        rot_y += dx * 0.5
        rot_x += dy * 0.5
        last_mouse_x = x
        last_mouse_y = y
        glutPostRedisplay()


def reshape(w, h):
    """Handles window resizing."""
    global window_width, window_height
    window_width = max(w, 1)
    window_height = max(h, 1)

    glViewport(0, 0, window_width, window_height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(window_width) / float(window_height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)


# ============================================================
# INITIALIZATION & CONSOLE OVERVIEW
# ============================================================

def print_academic_header():
    """Prints formatted experiment information to the console."""
    print("=" * 78)
    print(" EXPERIMENT - 6: IMPLEMENT THE Z-BUFFER ALGORITHM FOR HIDDEN SURFACE REMOVAL")
    print("=" * 78)
    print("Course Outcome: CO3 - Visible surface detection algorithms & 3D rendering")
    print("Bloom's Taxonomy Level: L3 - Apply")
    print("\nAIM:")
    print("  To implement the Z-Buffer (depth buffer) algorithm for hidden surface removal")
    print("  in OpenGL, analyzing depth testing, pixel-by-pixel depth comparisons,")
    print("  and resolving overlapping and intersecting polygons.")
    print("-" * 78)
    print("MATHEMATICAL FORMULATION:")
    print("  * Plane Equation:  A*x + B*y + C*z + D = 0")
    print("  * Depth Formula:   z = (-A*x - B*y - D) / C")
    print("  * Incremental:     Delta z = -A / C   (along each horizontal scanline step)")
    print("-" * 78)
    print("ALGORITHM FLOW:")
    print("  1. Initialize depth_buffer[x, y] = 1.0 (far plane) for all screen pixels.")
    print("  2. Initialize frame_buffer[x, y] = background_color.")
    print("  3. For each polygon P in the scene:")
    print("       For each pixel (x, y) covered by P:")
    print("         Calculate depth z(x, y)")
    print("         If z(x, y) < depth_buffer[x, y]:")
    print("             depth_buffer[x, y] = z(x, y)")
    print("             frame_buffer[x, y] = polygon_color")
    print("-" * 78)
    print("INTERACTIVE KEYBOARD CONTROLS:")
    print("  [Z]       : Toggle Z-Buffer ON / OFF (Witness hidden surface removal difference)")
    print("  [1]       : Scene 1 - Overlapping Polygons at different depths")
    print("  [2]       : Scene 2 - Intersecting Surfaces (Painter's algorithm failure)")
    print("  [3]       : Scene 3 - 3D Rotating Solid Objects (Cube & Pyramid)")
    print("  [4]       : Scene 4 - Discrete Software Z-Buffer Pixel & Depth Grid Simulation")
    print("  [O]       : Toggle Polygon Draw Submission Order (Front-to-Back vs Back-to-Front)")
    print("  [D]       : Toggle Depth Map Visualizer (Grayscale view)")
    print("  [Space]   : Toggle Auto-Rotation")
    print("  [Arrows]  : Rotate 3D Scene (or Left Click + Drag with Mouse)")
    print("  [+ / -]   : Zoom In / Zoom Out")
    print("  [R]       : Reset Camera View")
    print("  [H]       : Toggle HUD Overlay")
    print("  [Q / ESC] : Quit Application")
    print("=" * 78)


def init():
    """Initializes OpenGL context and rendering parameters."""
    glClearColor(0.08, 0.10, 0.14, 1.0)
    glClearDepth(1.0)

    # Enable depth test initially
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)

    # Enable smooth shading and perspective correction
    glShadeModel(GL_SMOOTH)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)


def main():
    """Main execution function."""
    print_academic_header()

    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)
    glutInitWindowPosition(100, 50)
    glutCreateWindow(b"Experiment 6: Z-Buffer Algorithm - Hidden Surface Removal")

    init()

    # Register GLUT callbacks
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    glutMouseFunc(mouse)
    glutMotionFunc(mouse_motion)
    glutIdleFunc(idle)

    print("\n[STATUS] OpenGL Window Launched Successfully.")
    print("[STATUS] Press 'Z' in the window to observe rendering with and without Z-Buffer!")

    glutMainLoop()


if __name__ == "__main__":
    main()
