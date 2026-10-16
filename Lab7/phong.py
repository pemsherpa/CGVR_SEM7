"""
===============================================================================
EXPERIMENT - 7: IMPLEMENT THE PHONG ILLUMINATION MODEL FOR A 3D OBJECT
===============================================================================
Course Outcome: CO3 - Apply 3D graphics concepts, illumination models (Phong),
                and shading techniques for realistic computer graphics rendering.
Bloom's Taxonomy Level: L3 - Apply

Aim:
To implement the Phong Illumination Model for 3D objects in OpenGL, analyzing
the individual contributions of Ambient, Diffuse, and Specular reflection 
components, specular exponents (shininess), light source positioning, 
and material properties.

Theoretical Background:
The Phong Illumination Model computes the reflected light intensity I at a 
surface point as the sum of three distinct components:
    I = I_ambient + I_diffuse + I_specular

Mathematical Formulation:
    I = k_a * I_a + k_d * I_d * (N . L) + k_s * I_s * (R . V)^n

Where:
    - I_a, I_d, I_s : Intensity of ambient, diffuse, and specular incident light.
    - k_a : Ambient reflection coefficient (0 <= k_a <= 1)
    - k_d : Diffuse reflection coefficient (0 <= k_d <= 1) [Lambert's Cosine Law]
    - k_s : Specular reflection coefficient (0 <= k_s <= 1) [Mirror-like highlight]
    - N   : Unit surface normal vector at the surface point
    - L   : Unit light direction vector pointing from surface to light source
    - R   : Unit reflection vector, calculated as: R = 2 * (N . L) * N - L
    - V   : Unit viewing direction vector pointing from surface to camera/eye
    - n   : Specular reflection exponent (shininess factor, typically 1 to 128+)
            Higher n produces smaller, sharper, tighter highlights (polished surface).
            Lower n produces broad, soft, spread-out highlights (dull surface).
===============================================================================
"""

import sys
import math
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *


# ============================================================
# GLOBAL CONFIGURATION & INTERACTION STATE
# ============================================================

window_width = 1000
window_height = 700

# Illumination component toggles
enable_ambient = True
enable_diffuse = True
enable_specular = True

# Shading model: GL_SMOOTH (Gouraud/Smooth) vs GL_FLAT (Faceted)
smooth_shading = True

# Active 3D object: 1: Sphere, 2: Teapot, 3: Torus, 4: Cube
current_object = 1

# Material preset index
current_material_idx = 0

# Shininess exponent (n)
shininess_exponent = 32.0

# 3D Camera / Object rotation
rot_x = 20.0
rot_y = -30.0
zoom_distance = -6.0
auto_rotate_object = False

# Light source position & animation
light_angle = 45.0
light_radius = 4.5
light_height = 3.0
auto_rotate_light = False
show_light_indicator = True
show_hud = True

# Mouse interaction variables
last_mouse_x = 0
last_mouse_y = 0
mouse_dragging = False


# ============================================================
# MATERIAL PRESETS (COEFFICIENTS k_a, k_d, k_s, n)
# ============================================================

MATERIALS = [
    {
        "name": "Gold",
        "ambient":   [0.24725, 0.1995,  0.0745,  1.0],
        "diffuse":   [0.75164, 0.60648, 0.22648, 1.0],
        "specular":  [0.62828, 0.55580, 0.36606, 1.0],
        "shininess": 51.2
    },
    {
        "name": "Emerald / Jade",
        "ambient":   [0.0215,  0.1745,  0.0215,  1.0],
        "diffuse":   [0.07568, 0.61424, 0.07568, 1.0],
        "specular":  [0.633,   0.72781, 0.633,   1.0],
        "shininess": 76.8
    },
    {
        "name": "Ruby / Red Plastic",
        "ambient":   [0.1745,  0.01175, 0.01175, 1.0],
        "diffuse":   [0.61424, 0.04136, 0.04136, 1.0],
        "specular":  [0.72781, 0.62696, 0.62696, 1.0],
        "shininess": 64.0
    },
    {
        "name": "Cyan Plastic",
        "ambient":   [0.0,     0.1,     0.06,    1.0],
        "diffuse":   [0.0,     0.5098,  0.5098,  1.0],
        "specular":  [0.502,   0.502,   0.502,   1.0],
        "shininess": 32.0
    },
    {
        "name": "Polished Silver",
        "ambient":   [0.19225, 0.19225, 0.19225, 1.0],
        "diffuse":   [0.50754, 0.50754, 0.50754, 1.0],
        "specular":  [0.50827, 0.50827, 0.50827, 1.0],
        "shininess": 51.2
    },
    {
        "name": "Brass",
        "ambient":   [0.32941, 0.22353, 0.02745, 1.0],
        "diffuse":   [0.78039, 0.56863, 0.11373, 1.0],
        "specular":  [0.99216, 0.94118, 0.80784, 1.0],
        "shininess": 27.8
    }
]


# ============================================================
# HUD TEXT OVERLAY UTILITIES
# ============================================================

def draw_text_2d(x, y, text, color=(1.0, 1.0, 1.0), font=GLUT_BITMAP_HELVETICA_12):
    """Renders 2D bitmap text overlay using screen pixel coordinates."""
    glColor3f(color[0], color[1], color[2])
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))


def render_hud():
    """Renders an informative on-screen HUD."""
    if not show_hud:
        return

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Disable lighting and depth testing for clean 2D text drawing
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)

    # Top Header Panel
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.06, 0.08, 0.12, 0.88)
    glBegin(GL_QUADS)
    glVertex2f(10, window_height - 10)
    glVertex2f(window_width - 10, window_height - 10)
    glVertex2f(window_width - 10, window_height - 95)
    glVertex2f(10, window_height - 95)
    glEnd()

    # Title & Theoretical Equation
    draw_text_2d(25, window_height - 35, 
                 "EXPERIMENT 7: PHONG ILLUMINATION MODEL FOR 3D OBJECTS", 
                 (0.98, 0.82, 0.25), GLUT_BITMAP_HELVETICA_18)
    draw_text_2d(25, window_height - 58, 
                 "Formula:  I = k_a * I_a  +  k_d * I_d * (N . L)  +  k_s * I_s * (R . V)^n", 
                 (0.40, 0.85, 1.00), GLUT_BITMAP_HELVETICA_12)
    draw_text_2d(25, window_height - 80, 
                 "Reflection Vector: R = 2 * (N . L) * N - L   |   Halfway Vector: H = (L + V) / |L + V|", 
                 (0.80, 0.80, 0.80), GLUT_BITMAP_HELVETICA_10)

    # Bottom Controls & Status Panel
    panel_h = 135
    glColor4f(0.06, 0.08, 0.12, 0.88)
    glBegin(GL_QUADS)
    glVertex2f(10, 10 + panel_h)
    glVertex2f(window_width - 10, 10 + panel_h)
    glVertex2f(window_width - 10, 10)
    glVertex2f(10, 10)
    glEnd()
    glDisable(GL_BLEND)

    # Status of Illumination Components
    amb_str  = "ON" if enable_ambient else "OFF"
    diff_str = "ON" if enable_diffuse else "OFF"
    spec_str = "ON" if enable_specular else "OFF"

    c_amb  = (0.2, 0.9, 0.4) if enable_ambient else (0.8, 0.3, 0.3)
    c_diff = (0.2, 0.9, 0.4) if enable_diffuse else (0.8, 0.3, 0.3)
    c_spec = (0.2, 0.9, 0.4) if enable_specular else (0.8, 0.3, 0.3)

    draw_text_2d(25, 120, f"[A] Ambient: {amb_str}", c_amb, GLUT_BITMAP_HELVETICA_12)
    draw_text_2d(170, 120, f"[D] Diffuse: {diff_str}", c_diff, GLUT_BITMAP_HELVETICA_12)
    draw_text_2d(315, 120, f"[S] Specular: {spec_str}", c_spec, GLUT_BITMAP_HELVETICA_12)

    mat_name = MATERIALS[current_material_idx]["name"]
    shading_name = "Smooth / Gouraud" if smooth_shading else "Flat (Faceted)"
    obj_names = ["Sphere", "Teapot", "Torus", "Cube"]
    draw_text_2d(460, 120, f"[M] Material: {mat_name}", (1.0, 0.8, 0.3), GLUT_BITMAP_HELVETICA_12)
    draw_text_2d(660, 120, f"[F] Shading: {shading_name}", (0.6, 0.9, 1.0), GLUT_BITMAP_HELVETICA_12)
    draw_text_2d(840, 120, f"[1-4] Obj: {obj_names[current_object-1]}", (0.9, 0.9, 0.9), GLUT_BITMAP_HELVETICA_12)

    # Shininess & Light Status
    draw_text_2d(25, 95, f"Shininess Exponent (n): {shininess_exponent:.1f}  (Use '[' or ']' to decrease/increase)", 
                 (0.95, 0.70, 0.30), GLUT_BITMAP_HELVETICA_12)
    light_status = "Orbiting (Auto)" if auto_rotate_light else "Static"
    draw_text_2d(520, 95, f"[L] Light Source: {light_status} (Pos: radius={light_radius:.1f}, angle={light_angle:.1f}°)", 
                 (0.85, 0.85, 0.85), GLUT_BITMAP_HELVETICA_10)

    # Controls instruction
    draw_text_2d(25, 65, "[A] Toggle Ambient  |  [D] Toggle Diffuse  |  [S] Toggle Specular  |  [M] Cycle Material  |  [F] Toggle Flat/Smooth", 
                 (0.95, 0.95, 0.95), GLUT_BITMAP_HELVETICA_10)
    draw_text_2d(25, 45, "[1-4] Switch 3D Model  |  [L] Toggle Orbiting Light  |  [Space] Auto-Spin Object  |  [[] / []] Adjust Shininess (n)", 
                 (0.80, 0.80, 0.80), GLUT_BITMAP_HELVETICA_10)
    draw_text_2d(25, 25, "[Mouse Drag / Arrows] Rotate View  |  [+/-] Zoom  |  [R] Reset View  |  [H] Toggle HUD Overlay", 
                 (0.65, 0.65, 0.65), GLUT_BITMAP_HELVETICA_10)

    # Restore matrix state
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)


# ============================================================
# LIGHTING SETUP & MATERIAL APPLICATION
# ============================================================

def setup_lighting():
    """Configures OpenGL Light 0 based on current component toggles and position."""
    # Compute current 3D position of the point light source
    rad = math.radians(light_angle)
    lx = light_radius * math.cos(rad)
    lz = light_radius * math.sin(rad)
    ly = light_height
    light_position = [lx, ly, lz, 1.0] # Positional point light (w=1.0)

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    # Ambient Light Component
    if enable_ambient:
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.25, 0.25, 0.25, 1.0])
    else:
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.0, 0.0, 0.0, 1.0])

    # Diffuse Light Component
    if enable_diffuse:
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.9, 0.9, 0.9, 1.0])
    else:
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.0, 0.0, 0.0, 1.0])

    # Specular Light Component
    if enable_specular:
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    else:
        glLightfv(GL_LIGHT0, GL_SPECULAR, [0.0, 0.0, 0.0, 1.0])

    # Set light position in world space
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)

    # Set shading model
    if smooth_shading:
        glShadeModel(GL_SMOOTH)
    else:
        glShadeModel(GL_FLAT)

    return lx, ly, lz


def apply_material():
    """Applies material reflection coefficients (k_a, k_d, k_s, n)."""
    mat = MATERIALS[current_material_idx]

    # Ambient reflection
    if enable_ambient:
        glMaterialfv(GL_FRONT, GL_AMBIENT, mat["ambient"])
    else:
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.0, 0.0, 0.0, 1.0])

    # Diffuse reflection
    if enable_diffuse:
        glMaterialfv(GL_FRONT, GL_DIFFUSE, mat["diffuse"])
    else:
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.0, 0.0, 0.0, 1.0])

    # Specular reflection
    if enable_specular:
        glMaterialfv(GL_FRONT, GL_SPECULAR, mat["specular"])
    else:
        glMaterialfv(GL_FRONT, GL_SPECULAR, [0.0, 0.0, 0.0, 1.0])

    # Shininess exponent (n)
    glMaterialf(GL_FRONT, GL_SHININESS, min(128.0, max(1.0, shininess_exponent)))


def draw_light_indicator(lx, ly, lz):
    """Draws a glowing sphere and directional beam indicating the light source position."""
    if not show_light_indicator:
        return

    glDisable(GL_LIGHTING)
    glPushMatrix()
    glTranslatef(lx, ly, lz)

    # Small bright yellow bulb
    glColor3f(1.0, 0.95, 0.3)
    glutSolidSphere(0.18, 16, 16)

    # Dashed ray pointing toward origin (object center)
    glColor4f(1.0, 0.9, 0.3, 0.4)
    glLineWidth(1.5)
    glBegin(GL_LINES)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(-lx * 0.8, -ly * 0.8, -lz * 0.8)
    glEnd()

    glPopMatrix()
    glEnable(GL_LIGHTING)


# ============================================================
# 3D OBJECT RENDERING
# ============================================================

def draw_3d_object():
    """Renders the selected 3D geometry with Phong illumination."""
    apply_material()

    if current_object == 1:
        # Smooth Sphere (optimal for viewing specular highlight curvature)
        glutSolidSphere(1.8, 64, 64)

    elif current_object == 2:
        # Utah Teapot (classic benchmark object with compound curves)
        glPushMatrix()
        glRotatef(30.0, 1.0, 0.0, 0.0)
        glutSolidTeapot(1.4)
        glPopMatrix()

    elif current_object == 3:
        # Torus (donut shape demonstrating inner/outer shadow boundaries)
        glPushMatrix()
        glRotatef(45.0, 1.0, 0.0, 0.0)
        glutSolidTorus(0.6, 1.4, 40, 60)
        glPopMatrix()

    elif current_object == 4:
        # Solid Cube (planar surfaces demonstrating flat/specular contrast)
        glutSolidCube(2.4)


def draw_ground_grid():
    """Draws an orientation reference grid."""
    glDisable(GL_LIGHTING)
    glColor4f(0.20, 0.25, 0.32, 0.35)
    glLineWidth(1.0)
    glBegin(GL_LINES)
    span = 6
    y_pos = -2.4
    for i in range(-span, span + 1):
        glVertex3f(float(i), y_pos, -float(span))
        glVertex3f(float(i), y_pos, float(span))
        glVertex3f(-float(span), y_pos, float(i))
        glVertex3f(float(span), y_pos, float(i))
    glEnd()
    glEnable(GL_LIGHTING)


# ============================================================
# MAIN DISPLAY CALLBACK
# ============================================================

def display():
    """Main rendering callback."""
    glClearColor(0.06, 0.08, 0.12, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Apply 3D Camera zoom
    glTranslatef(0.0, 0.0, zoom_distance)

    # Position Light in Camera/World space
    lx, ly, lz = setup_lighting()

    # Draw Light Source Indicator
    draw_light_indicator(lx, ly, lz)

    # Apply user rotation to the 3D scene / object
    glRotatef(rot_x, 1.0, 0.0, 0.0)
    glRotatef(rot_y, 0.0, 1.0, 0.0)

    # Reference grid
    draw_ground_grid()

    # Render illuminated 3D geometry
    draw_3d_object()

    # Render on-screen HUD
    render_hud()

    glutSwapBuffers()


# ============================================================
# ANIMATION & INTERACTION HANDLERS
# ============================================================

def idle():
    """Continuous idle callback for auto-rotation and light orbiting."""
    global rot_y, light_angle
    changed = False

    if auto_rotate_object:
        rot_y = (rot_y + 0.6) % 360.0
        changed = True

    if auto_rotate_light:
        light_angle = (light_angle + 1.2) % 360.0
        changed = True

    if changed:
        glutPostRedisplay()


def keyboard(key, x, y):
    """Handles keyboard inputs."""
    global enable_ambient, enable_diffuse, enable_specular
    global smooth_shading, current_object, current_material_idx
    global shininess_exponent, auto_rotate_object, auto_rotate_light
    global show_hud, rot_x, rot_y, zoom_distance

    ch = key.decode("utf-8") if isinstance(key, bytes) else key

    if ch in ('a', 'A'):
        enable_ambient = not enable_ambient
        print(f"\n[EVENT] Ambient Component: {'ENABLED' if enable_ambient else 'DISABLED'}")

    elif ch in ('d', 'D'):
        enable_diffuse = not enable_diffuse
        print(f"\n[EVENT] Diffuse Component: {'ENABLED' if enable_diffuse else 'DISABLED'}")

    elif ch in ('s', 'S'):
        enable_specular = not enable_specular
        print(f"\n[EVENT] Specular Component: {'ENABLED' if enable_specular else 'DISABLED'}")

    elif ch in ('f', 'F'):
        smooth_shading = not smooth_shading
        print(f"\n[EVENT] Shading Model: {'SMOOTH (Gouraud)' if smooth_shading else 'FLAT (Faceted)'}")

    elif ch in ('m', 'M'):
        current_material_idx = (current_material_idx + 1) % len(MATERIALS)
        shininess_exponent = MATERIALS[current_material_idx]["shininess"]
        print(f"\n[EVENT] Selected Material: {MATERIALS[current_material_idx]['name']} (n={shininess_exponent})")

    elif ch in ('1', '2', '3', '4'):
        current_object = int(ch)
        names = ["Sphere", "Teapot", "Torus", "Cube"]
        print(f"\n[EVENT] Selected 3D Object: {names[current_object-1]}")

    elif ch in ('l', 'L'):
        auto_rotate_light = not auto_rotate_light
        print(f"\n[EVENT] Orbiting Light: {'ON' if auto_rotate_light else 'OFF'}")

    elif ch == ' ':
        auto_rotate_object = not auto_rotate_object
        print(f"\n[EVENT] Auto-Rotation: {'ON' if auto_rotate_object else 'OFF'}")

    elif ch == ']':
        shininess_exponent = min(128.0, shininess_exponent * 1.5)
        print(f"\n[EVENT] Shininess Exponent increased to: {shininess_exponent:.1f}")

    elif ch == '[':
        shininess_exponent = max(1.0, shininess_exponent / 1.5)
        print(f"\n[EVENT] Shininess Exponent decreased to: {shininess_exponent:.1f}")

    elif ch in ('h', 'H'):
        show_hud = not show_hud

    elif ch in ('r', 'R'):
        rot_x = 20.0
        rot_y = -30.0
        zoom_distance = -6.0
        shininess_exponent = MATERIALS[current_material_idx]["shininess"]
        print("\n[EVENT] Camera and settings reset.")

    elif ch in ('+', '='):
        zoom_distance += 0.5
    elif ch in ('-', '_'):
        zoom_distance -= 0.5

    elif ch in ('\x1b', 'q', 'Q'):
        print("\n[INFO] Exiting Program. Thank you!")
        sys.exit(0)

    glutPostRedisplay()


def special_keys(key, x, y):
    """Handles arrow keys for view rotation."""
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
    """Handles mouse click events."""
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
    print(" EXPERIMENT - 7: IMPLEMENT THE PHONG ILLUMINATION MODEL FOR A 3D OBJECT")
    print("=" * 78)
    print("Course Outcome: CO3 - Illumination Models & Realistic 3D Rendering")
    print("Bloom's Taxonomy Level: L3 - Apply")
    print("\nAIM:")
    print("  To implement the Phong Illumination Model for 3D objects in OpenGL,")
    print("  analyzing the three constituent reflection components:")
    print("  1. Ambient (Background ambient light)")
    print("  2. Diffuse (Lambertian directional reflection)")
    print("  3. Specular (Glossy highlight dependent on viewer orientation)")
    print("-" * 78)
    print("MATHEMATICAL FORMULATION:")
    print("  * Total Intensity: I = I_ambient + I_diffuse + I_specular")
    print("  * Expanded:        I = k_a*I_a + k_d*I_d*(N . L) + k_s*I_s*(R . V)^n")
    print("  * Reflection:      R = 2 * (N . L) * N - L")
    print("-" * 78)
    print("INTERACTIVE KEYBOARD CONTROLS:")
    print("  [A]       : Toggle Ambient Component (k_a * I_a)")
    print("  [D]       : Toggle Diffuse Component (k_d * I_d * (N . L))")
    print("  [S]       : Toggle Specular Component (k_s * I_s * (R . V)^n)")
    print("  [M]       : Cycle Material Presets (Gold, Emerald, Ruby, Silver, Brass)")
    print("  [F]       : Toggle Shading Model: Smooth (Gouraud) vs Flat")
    print("  [1] - [4] : Switch 3D Object (1: Sphere, 2: Teapot, 3: Torus, 4: Cube)")
    print("  [L]       : Toggle Orbiting / Moving Light Source Animation")
    print("  [Space]   : Toggle 3D Object Auto-Rotation")
    print("  [ [ / ] ] : Decrease / Increase Specular Shininess Exponent (n)")
    print("  [Arrows]  : Rotate 3D Object (or Left Click + Drag with Mouse)")
    print("  [+ / -]   : Zoom In / Zoom Out")
    print("  [R]       : Reset Camera & Parameters to Default")
    print("  [H]       : Toggle On-Screen HUD Overlay")
    print("  [Q / ESC] : Quit Application")
    print("=" * 78)


def init():
    """Initializes OpenGL rendering state."""
    glClearColor(0.06, 0.08, 0.12, 1.0)
    glClearDepth(1.0)

    # Enable Z-Buffer depth testing
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)

    # Automatically normalize normals after scaling/transformations
    glEnable(GL_NORMALIZE)

    # Enable color material tracking
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT, GL_DIFFUSE)

    # Enable smooth shading
    glShadeModel(GL_SMOOTH)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)


def main():
    """Main execution function."""
    print_academic_header()

    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)
    glutInitWindowPosition(100, 50)
    glutCreateWindow(b"Experiment 7: Phong Illumination Model - 3D Object")

    init()

    # Register callbacks
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    glutMouseFunc(mouse)
    glutMotionFunc(mouse_motion)
    glutIdleFunc(idle)

    print("\n[STATUS] OpenGL Window Launched Successfully.")
    print("[STATUS] Press 'A', 'D', 'S' to isolate Phong illumination components!")

    glutMainLoop()


if __name__ == "__main__":
    main()
