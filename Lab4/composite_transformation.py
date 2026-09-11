"""
===============================================================================
EXPERIMENT - 4: COMPOSITE TRANSFORMATIONS USING MATRIX REPRESENTATION
===============================================================================
Course Outcome: CO2 - Apply two-dimensional graphics transformations using matrix 
                representation and homogeneous coordinates for graphical object manipulation.
Bloom's Taxonomy Level: L3 - Apply

Aim:
To implement fundamental and composite 2D geometric transformations using 
homogeneous coordinate representation and transformation matrices in OpenGL.

Transformations Implemented:
1. Fundamental Transformations: Translation, Rotation, Scaling, Reflection, Shearing
2. Composite Transformations: 
   - Rotation about an arbitrary point (xr, yr)
   - Scaling about an arbitrary point (xf, yf)
   - Custom composite transformation sequence (concatenated matrix pipeline)
===============================================================================
"""

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import numpy as np
import sys


# ============================================================
# GLOBAL VARIABLES
# ============================================================

object_type = 1
transformation_type = 1

points = []
transformed_points = []
composite_matrix = np.identity(3, dtype=float)
transformation_name = "Identity"


# ============================================================
# MATRIX GENERATORS FOR HOMOGENEOUS 2D TRANSFORMATIONS (3x3)
# ============================================================

def get_translation_matrix(tx, ty):
    """
    Returns 3x3 Translation Matrix in Homogeneous Coordinates.
    | 1  0  tx |
    | 0  1  ty |
    | 0  0   1 |
    """
    return np.array([
        [1.0, 0.0, float(tx)],
        [0.0, 1.0, float(ty)],
        [0.0, 0.0, 1.0]
    ], dtype=float)


def get_rotation_matrix(angle_deg):
    """
    Returns 3x3 Rotation Matrix in Homogeneous Coordinates (Counter-Clockwise).
    | cos(theta) -sin(theta)  0 |
    | sin(theta)  cos(theta)  0 |
    |     0           0       1 |
    """
    rad = math.radians(angle_deg)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)

    return np.array([
        [cos_a, -sin_a, 0.0],
        [sin_a,  cos_a, 0.0],
        [0.0,    0.0,   1.0]
    ], dtype=float)


def get_scaling_matrix(sx, sy):
    """
    Returns 3x3 Scaling Matrix in Homogeneous Coordinates.
    | sx  0  0 |
    |  0 sy  0 |
    |  0  0  1 |
    """
    return np.array([
        [float(sx), 0.0,       0.0],
        [0.0,       float(sy), 0.0],
        [0.0,       0.0,       1.0]
    ], dtype=float)


def get_reflection_matrix(choice):
    """
    Returns 3x3 Reflection Matrix for different reflection axes.
    Choice 1: About X-axis (y -> -y)
    Choice 2: About Y-axis (x -> -x)
    Choice 3: About Origin (x -> -x, y -> -y)
    Choice 4: About line y = x
    Choice 5: About line y = -x
    """
    if choice == 1:  # X-axis
        return np.array([
            [1.0,  0.0, 0.0],
            [0.0, -1.0, 0.0],
            [0.0,  0.0, 1.0]
        ], dtype=float)

    elif choice == 2:  # Y-axis
        return np.array([
            [-1.0, 0.0, 0.0],
            [ 0.0, 1.0, 0.0],
            [ 0.0, 0.0, 1.0]
        ], dtype=float)

    elif choice == 3:  # Origin
        return np.array([
            [-1.0,  0.0, 0.0],
            [ 0.0, -1.0, 0.0],
            [ 0.0,  0.0, 1.0]
        ], dtype=float)

    elif choice == 4:  # y = x
        return np.array([
            [0.0, 1.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0]
        ], dtype=float)

    elif choice == 5:  # y = -x
        return np.array([
            [ 0.0, -1.0, 0.0],
            [-1.0,  0.0, 0.0],
            [ 0.0,  0.0, 1.0]
        ], dtype=float)

    return np.identity(3, dtype=float)


def get_shearing_matrix(sh_x, sh_y):
    """
    Returns 3x3 Shearing Matrix in Homogeneous Coordinates.
    | 1     sh_x  0 |
    | sh_y  1     0 |
    | 0     0     1 |
    """
    return np.array([
        [1.0,       float(sh_x), 0.0],
        [float(sh_y), 1.0,       0.0],
        [0.0,         0.0,       1.0]
    ], dtype=float)


# ============================================================
# APPLY HOMOGENEOUS MATRIX TRANSFORMATION
# ============================================================

def transform_point(matrix, pt):
    """
    Applies 3x3 transformation matrix to 2D point using homogeneous coordinates.
    P' = M * P where P = [x, y, 1]^T
    """
    v = np.array([pt[0], pt[1], 1.0], dtype=float)
    v_prime = np.matmul(matrix, v)
    return (float(v_prime[0]), float(v_prime[1]))


def apply_transformation():
    """
    Builds the composite transformation matrix M based on user selection,
    prints matrix operations to console, and transforms all object points.
    """
    global transformed_points, composite_matrix, transformation_name

    composite_matrix = np.identity(3, dtype=float)

    print("\n" + "=" * 60)
    print("           COMPOSITE TRANSFORMATION MATRIX BUILDER")
    print("=" * 60)

    # 1. TRANSLATION
    if transformation_type == 1:
        tx = float(input("Enter translation offset tx: "))
        ty = float(input("Enter translation offset ty: "))
        composite_matrix = get_translation_matrix(tx, ty)
        transformation_name = f"Translation (tx={tx}, ty={ty})"

    # 2. ROTATION (ABOUT ORIGIN)
    elif transformation_type == 2:
        angle = float(input("Enter rotation angle in degrees: "))
        composite_matrix = get_rotation_matrix(angle)
        transformation_name = f"Rotation ({angle}° about origin)"

    # 3. SCALING (ABOUT ORIGIN)
    elif transformation_type == 3:
        sx = float(input("Enter scaling factor sx: "))
        sy = float(input("Enter scaling factor sy: "))
        composite_matrix = get_scaling_matrix(sx, sy)
        transformation_name = f"Scaling (sx={sx}, sy={sy})"

    # 4. REFLECTION
    elif transformation_type == 4:
        print("\nReflection Options:")
        print("1. Reflection about X-axis")
        print("2. Reflection about Y-axis")
        print("3. Reflection about Origin")
        print("4. Reflection about line y = x")
        print("5. Reflection about line y = -x")
        choice = int(input("Enter reflection choice (1-5): "))
        composite_matrix = get_reflection_matrix(choice)
        names = ["X-axis", "Y-axis", "Origin", "y = x", "y = -x"]
        transformation_name = f"Reflection about {names[choice-1]}"

    # 5. SHEARING
    elif transformation_type == 5:
        sh_x = float(input("Enter X-shear factor (sh_x, 0 for none): "))
        sh_y = float(input("Enter Y-shear factor (sh_y, 0 for none): "))
        composite_matrix = get_shearing_matrix(sh_x, sh_y)
        transformation_name = f"Shearing (sh_x={sh_x}, sh_y={sh_y})"

    # 6. COMPOSITE: ROTATION ABOUT ARBITRARY POINT (xr, yr)
    elif transformation_type == 6:
        print("\n--- COMPOSITE TRANSFORMATION: Rotation about Arbitrary Point ---")
        print("Mathematical Formula: M = T(xr, yr) * R(theta) * T(-xr, -yr)")
        xr = float(input("Enter arbitrary pivot x-coordinate (xr): "))
        yr = float(input("Enter arbitrary pivot y-coordinate (yr): "))
        angle = float(input("Enter rotation angle in degrees: "))

        T_neg = get_translation_matrix(-xr, -yr)
        R = get_rotation_matrix(angle)
        T_pos = get_translation_matrix(xr, yr)

        # Concatenate matrices: M = T(xr, yr) . R(theta) . T(-xr, -yr)
        composite_matrix = np.matmul(T_pos, np.matmul(R, T_neg))
        transformation_name = f"Composite Rotation ({angle}° about ({xr}, {yr}))"

    # 7. COMPOSITE: SCALING ABOUT ARBITRARY POINT (xf, yf)
    elif transformation_type == 7:
        print("\n--- COMPOSITE TRANSFORMATION: Scaling about Arbitrary Point ---")
        print("Mathematical Formula: M = T(xf, yf) * S(sx, sy) * T(-xf, -yf)")
        xf = float(input("Enter arbitrary fixed x-coordinate (xf): "))
        yf = float(input("Enter arbitrary fixed y-coordinate (yf): "))
        sx = float(input("Enter scaling factor sx: "))
        sy = float(input("Enter scaling factor sy: "))

        T_neg = get_translation_matrix(-xf, -yf)
        S = get_scaling_matrix(sx, sy)
        T_pos = get_translation_matrix(xf, yf)

        # Concatenate matrices: M = T(xf, yf) . S(sx, sy) . T(-xf, -yf)
        composite_matrix = np.matmul(T_pos, np.matmul(S, T_neg))
        transformation_name = f"Composite Scaling (sx={sx}, sy={sy} about ({xf}, {yf}))"

    # 8. COMPOSITE: GENERAL CUSTOM SEQUENCE PIPELINE
    elif transformation_type == 8:
        print("\n--- COMPOSITE TRANSFORMATION: Custom Transformation Pipeline ---")
        num_steps = int(input("Enter number of transformations to combine: "))

        matrices = []
        descriptions = []

        for k in range(1, num_steps + 1):
            print(f"\nStep {k}: Choose transformation:")
            print("  1. Translation")
            print("  2. Rotation")
            print("  3. Scaling")
            print("  4. Reflection")
            print("  5. Shearing")
            st = int(input(f"  Enter choice for Step {k}: "))

            if st == 1:
                tx = float(input("    Enter tx: "))
                ty = float(input("    Enter ty: "))
                matrices.append(get_translation_matrix(tx, ty))
                descriptions.append(f"T({tx},{ty})")
            elif st == 2:
                ang = float(input("    Enter angle: "))
                matrices.append(get_rotation_matrix(ang))
                descriptions.append(f"R({ang}°)")
            elif st == 3:
                sx = float(input("    Enter sx: "))
                sy = float(input("    Enter sy: "))
                matrices.append(get_scaling_matrix(sx, sy))
                descriptions.append(f"S({sx},{sy})")
            elif st == 4:
                ch = int(input("    Enter reflection choice (1:X, 2:Y, 3:Origin, 4:y=x, 5:y=-x): "))
                matrices.append(get_reflection_matrix(ch))
                descriptions.append(f"Reflect({ch})")
            elif st == 5:
                shx = float(input("    Enter sh_x: "))
                shy = float(input("    Enter sh_y: "))
                matrices.append(get_shearing_matrix(shx, shy))
                descriptions.append(f"Shear({shx},{shy})")

        # Combine matrices in application order: M_composite = M_n . ... . M_2 . M_1
        composite_matrix = np.identity(3, dtype=float)
        for M in matrices:
            composite_matrix = np.matmul(M, composite_matrix)

        transformation_name = "Pipeline: " + " -> ".join(descriptions)

    # Print Final Composite Matrix M to Console
    print("\n" + "-" * 50)
    print("Final Composite 3x3 Homogeneous Transformation Matrix M:")
    print("-" * 50)
    for row in composite_matrix:
        print(f"  [ {row[0]:8.4f}  {row[1]:8.4f}  {row[2]:8.4f} ]")
    print("-" * 50)

    # Apply M to all vertices
    transformed_points = [transform_point(composite_matrix, pt) for pt in points]

    print("\nOriginal Points vs Transformed Points:")
    for orig, trans in zip(points, transformed_points):
        print(f"  Original: ({orig[0]:.2f}, {orig[1]:.2f})  -->  Transformed: ({trans[0]:.2f}, {trans[1]:.2f})")
    print("=" * 60 + "\n")


# ============================================================
# RENDERING & DRAWING HELPERS
# ============================================================

def draw_text(x, y, text):
    """Draw text at 2D raster coordinates."""
    glRasterPos2f(x, y)
    for character in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(character))


def draw_grid():
    """Draw coordinate grid, axes, gridlines, and numeric markings."""
    # Minor Gridlines
    glColor3f(0.88, 0.88, 0.88)
    glLineWidth(1.0)
    glBegin(GL_LINES)
    for i in range(-20, 21):
        # Vertical grid line
        glVertex2f(i, -20)
        glVertex2f(i, 20)
        # Horizontal grid line
        glVertex2f(-20, i)
        glVertex2f(20, i)
    glEnd()

    # Major X and Y Axes
    glColor3f(0.1, 0.1, 0.1)
    glLineWidth(2.0)
    glBegin(GL_LINES)
    # X-axis
    glVertex2f(-20, 0)
    glVertex2f(20, 0)
    # Y-axis
    glVertex2f(0, -20)
    glVertex2f(0, 20)
    glEnd()
    glLineWidth(1.0)

    # Axis Labels
    glColor3f(0.0, 0.0, 0.0)
    draw_text(19.2, 0.4, "X")
    draw_text(0.4, 19.2, "Y")

    # Tick Mark Labels
    for i in range(-20, 21, 2):
        if i != 0:
            draw_text(i - 0.3, -0.8, str(i))
            draw_text(0.3, i - 0.3, str(i))


def draw_shape(pts, color, label_prefix=""):
    """
    Draw point, line, triangle, or polygon based on list of vertices.
    """
    glColor3fv(color)
    num_pts = len(pts)

    if num_pts == 1:
        glPointSize(8.0)
        glBegin(GL_POINTS)
        glVertex2f(pts[0][0], pts[0][1])
        glEnd()
        glPointSize(1.0)
        draw_text(pts[0][0] + 0.3, pts[0][1] + 0.3, f"{label_prefix}({pts[0][0]:.1f},{pts[0][1]:.1f})")

    elif num_pts == 2:
        glLineWidth(2.5)
        glBegin(GL_LINES)
        glVertex2f(pts[0][0], pts[0][1])
        glVertex2f(pts[1][0], pts[1][1])
        glEnd()
        glLineWidth(1.0)
        for idx, p in enumerate(pts):
            draw_text(p[0] + 0.3, p[1] + 0.3, f"{label_prefix}P{idx+1}({p[0]:.1f},{p[1]:.1f})")

    elif num_pts >= 3:
        glLineWidth(2.5)
        glBegin(GL_LINE_LOOP)
        for p in pts:
            glVertex2f(p[0], p[1])
        glEnd()
        glLineWidth(1.0)

        for idx, p in enumerate(pts):
            draw_text(p[0] + 0.3, p[1] + 0.3, f"{label_prefix}P{idx+1}({p[0]:.1f},{p[1]:.1f})")


def display():
    """Main OpenGL Display callback."""
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()

    # 1. Render Grid
    draw_grid()

    # 2. Render Original Shape (BLUE)
    draw_shape(points, [0.0, 0.3, 0.9], "Orig ")

    # 3. Render Transformed Shape (RED)
    draw_shape(transformed_points, [0.9, 0.1, 0.1], "Trans ")

    # 4. Render Legend and Information overlay
    glColor3f(0.0, 0.3, 0.9)
    draw_text(-19.5, 19.0, "BLUE : Original Object")

    glColor3f(0.9, 0.1, 0.1)
    draw_text(-19.5, 18.0, "RED  : Transformed Object (Homogeneous Matrix)")

    glColor3f(0.1, 0.1, 0.1)
    draw_text(-19.5, 17.0, f"Transformation: {transformation_name}")

    # Display 3x3 Matrix on screen
    draw_text(-19.5, 15.8, "Composite Matrix M [3x3]:")
    draw_text(-19.5, 14.8, f"| {composite_matrix[0][0]:6.2f} {composite_matrix[0][1]:6.2f} {composite_matrix[0][2]:6.2f} |")
    draw_text(-19.5, 13.8, f"| {composite_matrix[1][0]:6.2f} {composite_matrix[1][1]:6.2f} {composite_matrix[1][2]:6.2f} |")
    draw_text(-19.5, 12.8, f"| {composite_matrix[2][0]:6.2f} {composite_matrix[2][1]:6.2f} {composite_matrix[2][2]:6.2f} |")

    glFlush()


# ============================================================
# INITIALIZATION & USER INPUT INTERFACE
# ============================================================

def init():
    """Initialize OpenGL viewing area and background color."""
    glClearColor(1.0, 1.0, 1.0, 1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(-20.0, 20.0, -20.0, 20.0)
    glMatrixMode(GL_MODELVIEW)


def get_input():
    """Interactive command-line interface for selecting object and transformations."""
    global object_type, transformation_type, points

    print("=======================================================================")
    print("   EXPERIMENT 4: 2D COMPOSITE TRANSFORMATIONS VIA HOMOGENEOUS MATRICES")
    print("=======================================================================")
    print("\nSelect 2D Geometric Object:")
    print("  1. Point")
    print("  2. Line Segment")
    print("  3. Triangle")
    print("  4. Rectangle / Square")
    print("  5. House Shape (5-vertex polygon)")

    object_type = int(input("\nEnter object choice (1-5): "))

    if object_type == 1:
        x = float(input("Enter point x: "))
        y = float(input("Enter point y: "))
        points = [(x, y)]

    elif object_type == 2:
        print("\nEnter Line Endpoints:")
        x1 = float(input("Point 1 x1: "))
        y1 = float(input("Point 1 y1: "))
        x2 = float(input("Point 2 x2: "))
        y2 = float(input("Point 2 y2: "))
        points = [(x1, y1), (x2, y2)]

    elif object_type == 3:
        print("\nEnter Triangle Vertices:")
        x1, y1 = float(input("P1 x: ")), float(input("P1 y: "))
        x2, y2 = float(input("P2 x: ")), float(input("P2 y: "))
        x3, y3 = float(input("P3 x: ")), float(input("P3 y: "))
        points = [(x1, y1), (x2, y2), (x3, y3)]

    elif object_type == 4:
        print("\nEnter Rectangle Vertices (Bottom-Left & Top-Right):")
        xmin = float(input("x-min: "))
        ymin = float(input("y-min: "))
        xmax = float(input("x-max: "))
        ymax = float(input("y-max: "))
        points = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]

    elif object_type == 5:
        # Default house shape
        print("\nUsing standard 5-vertex House shape at center.")
        points = [(2, 2), (6, 2), (6, 6), (4, 9), (2, 6)]

    else:
        print("Invalid choice, defaulting to Triangle (2,2), (6,2), (4,6)")
        points = [(2.0, 2.0), (6.0, 2.0), (4.0, 6.0)]

    print("\nSelect Transformation Type:")
    print("  --- Fundamental Transformations ---")
    print("  1. Translation T(tx, ty)")
    print("  2. Rotation R(theta) about Origin")
    print("  3. Scaling S(sx, sy) about Origin")
    print("  4. Reflection")
    print("  5. Shearing SH(sh_x, sh_y)")
    print("  --- Composite Transformations ---")
    print("  6. Composite: Rotation about an Arbitrary Point (xr, yr)")
    print("  7. Composite: Scaling about an Arbitrary Point (xf, yf)")
    print("  8. Composite: Custom Multi-Step Pipeline Concatenation")

    transformation_type = int(input("\nEnter transformation choice (1-8): "))
    apply_transformation()


# ============================================================
# MAIN ENTRY POINT
# ============================================================

def main():
    get_input()

    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    glutInitWindowSize(900, 700)
    glutInitWindowPosition(100, 50)
    glutCreateWindow(b"Experiment 4 - 2D Composite Transformations Matrix Representation")

    init()
    glutDisplayFunc(display)
    glutMainLoop()


if __name__ == "__main__":
    main()
