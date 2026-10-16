# EXPERIMENT – 7: IMPLEMENT THE PHONG ILLUMINATION MODEL FOR A 3D OBJECT

## Aim
To implement the **Phong Illumination Model** for 3D objects using OpenGL, analyzing the contributions of ambient, diffuse, and specular reflection, material properties ($k_a, k_d, k_s$), specular exponent / shininess ($n$), light source positioning, and shading techniques (Flat vs Smooth/Gouraud).

## Course Outcome
**CO3:** Apply 3D graphics concepts, illumination models (Phong), and surface shading techniques for realistic computer graphics rendering.

## Bloom's Taxonomy Level
**L3 – Apply**

## Learning Objectives
After completing this experiment, the student will be able to:
1. Understand the physics of light-surface interactions in 3D computer graphics.
2. Formulate and compute the three components of the **Phong Illumination Model**:
   - Ambient Reflection
   - Diffuse Reflection (Lambert's Cosine Law)
   - Specular Reflection (Phong Highlight)
3. Derive and calculate the **Reflection Vector** ($\mathbf{R}$) and understand the **Blinn-Phong Halfway Vector** ($\mathbf{H}$).
4. Evaluate the effect of the **specular reflection exponent** ($n$) on highlight tightness and surface glossiness.
5. Distinguish between different surface shading models: **Flat Shading**, **Gouraud Shading**, and **Phong Shading**.
6. Develop OpenGL programs using `glLightfv`, `glMaterialfv`, `glMaterialf`, and `glShadeModel`.

---

## Theoretical Background & Mathematical Formulations

### 1. The Phong Illumination Model Overview
Developed by Bui Tuong Phong in 1975, the Phong Illumination Model is an empirical model that approximates the reflection of light from surface points in 3D space. The total reflected light intensity $I$ is calculated as the linear superposition of three terms:

$$I = I_{\text{ambient}} + I_{\text{diffuse}} + I_{\text{specular}}$$

$$\mathbf{I = k_a \cdot I_a + k_d \cdot I_d \cdot (\mathbf{N} \cdot \mathbf{L}) + k_s \cdot I_s \cdot (\mathbf{R} \cdot \mathbf{V})^n}$$

Where:
- $I_a, I_d, I_s$: Intensities of ambient, diffuse, and specular components of the light source.
- $k_a$: Ambient reflection coefficient ($0 \le k_a \le 1$).
- $k_d$: Diffuse reflection coefficient ($0 \le k_d \le 1$).
- $k_s$: Specular reflection coefficient ($0 \le k_s \le 1$).
- $\mathbf{N}$: Unit surface normal vector at the surface point.
- $\mathbf{L}$: Unit light source vector pointing from the surface point toward the light source.
- $\mathbf{R}$: Unit reflection direction vector.
- $\mathbf{V}$: Unit viewing vector pointing from the surface point toward the camera/eye.
- $n$: Specular reflection exponent (shininess parameter, typically $1 \le n \le 128$).

---

### 2. Detailed Component Breakdown

#### A. Ambient Reflection ($I_{\text{ambient}} = k_a \cdot I_a$)
- Represents background light that has undergone multiple diffuse reflections from surrounding surfaces (inter-object reflections).
- It illuminates all surfaces equally from all directions and does not depend on surface orientation or light position.

#### B. Diffuse Reflection ($I_{\text{diffuse}} = k_d \cdot I_d \cdot (\mathbf{N} \cdot \mathbf{L})$)
- Governed by **Lambert's Cosine Law**: The reflected intensity is directly proportional to the cosine of the angle of incidence $\theta$ between the surface normal $\mathbf{N}$ and the light vector $\mathbf{L}$:
  $$\cos\theta = \mathbf{N} \cdot \mathbf{L}$$
- If $\mathbf{N} \cdot \mathbf{L} \le 0$, the light source is behind the surface, so diffuse reflection is zero.
- Diffuse surfaces (like chalk, matte paper) scatter light equally in all directions, so brightness does **not** depend on viewer position $\mathbf{V}$.

#### C. Specular Reflection ($I_{\text{specular}} = k_s \cdot I_s \cdot (\mathbf{R} \cdot \mathbf{V})^n$)
- Models mirror-like glossy highlights observed on shiny surfaces (metal, plastic, polished apple).
- Maximum reflection occurs in the ideal reflection direction $\mathbf{R}$.
- As the angle $\phi$ between the reflection vector $\mathbf{R}$ and the viewing vector $\mathbf{V}$ increases, specular intensity drops off rapidly according to $\cos^n\phi = (\mathbf{R} \cdot \mathbf{V})^n$.

#### D. Mathematical Derivation of the Reflection Vector $\mathbf{R}$
Given unit surface normal $\mathbf{N}$ and unit incident light vector $\mathbf{L}$:
$$\mathbf{R} = 2(\mathbf{N} \cdot \mathbf{L})\mathbf{N} - \mathbf{L}$$

#### E. Blinn-Phong Variation (Halfway Vector $\mathbf{H}$)
Jim Blinn introduced an optimization used by OpenGL's fixed-function pipeline using the halfway vector $\mathbf{H}$ between $\mathbf{L}$ and $\mathbf{V}$:
$$\mathbf{H} = \frac{\mathbf{L} + \mathbf{V}}{\|\mathbf{L} + \mathbf{V}\|}$$
The specular term becomes $(\mathbf{N} \cdot \mathbf{H})^{n'}$. When the light source and viewer are at infinity, $\mathbf{H}$ is constant, making this formulation much faster to compute.

---

### 3. Surface Shading Models Comparison

| Shading Technique | Normal Computation | Calculation Point | Visual Result & Cost |
| :--- | :--- | :--- | :--- |
| **Flat Shading** (`GL_FLAT`) | One normal per polygon face | Evaluated once per polygon | Faceted appearance; Mach banding along edges; very fast. |
| **Gouraud Shading** (`GL_SMOOTH`) | Vertex normals computed | Illumination evaluated at vertices, linearly interpolated across pixels | Smooth appearance; can miss specular highlights in large polygons. |
| **Phong Shading** | Vertex normals interpolated per pixel | Illumination evaluated at every single pixel | High fidelity highlights; accurate specular reflections; higher GPU cost. |

---

## File Structure & How to Run

```
CGVR_SEM7/
├── Lab7/
│   ├── phong.py        # Main OpenGL + GLUT implementation
│   └── README.md       # Lab documentation, theory, viva & assignment answers
```

### Execution Command

```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Run Experiment 7
python Lab7/phong.py
```

### Interactive Keyboard & Mouse Controls

| Key / Action | Function |
| :--- | :--- |
| **`A`** | **Toggle Ambient Reflection ($I_{\text{ambient}}$) ON / OFF** |
| **`D`** | **Toggle Diffuse Reflection ($I_{\text{diffuse}}$) ON / OFF** |
| **`S`** | **Toggle Specular Reflection ($I_{\text{specular}}$) ON / OFF** |
| **`M`** | Cycle Material Presets (Gold, Emerald/Jade, Ruby, Cyan Plastic, Silver, Brass) |
| **`F`** | Toggle Shading Model: Smooth (Gouraud) vs Flat (Faceted) |
| **`1` – `4`** | Select 3D Geometry (1: Sphere, 2: Teapot, 3: Torus, 4: Cube) |
| **`L`** | Toggle Orbiting Point Light Source Animation |
| **`[` / `]`** | Decrease / Increase Shininess Exponent ($n$) |
| **`Space`** | Toggle 3D Object Auto-Rotation |
| **Arrow Keys / Mouse Drag** | Rotate Scene freely in 3D |
| **`+` / `-`** | Zoom In / Zoom Out |
| **`R`** | Reset Camera and parameters to default |
| **`H`** | Toggle On-Screen Heads-Up Display (HUD) |
| **`Q` / `ESC`** | Quit Application |

---

## Solutions to Viva Questions

### 61. What is a geometric transformation?
A geometric transformation is an operation that alters the coordinate positions, orientation, size, or shape of an object in a graphics coordinate system. The basic geometric transformations in 2D and 3D are translation, rotation, scaling, reflection, and shearing.

### 62. Why are homogeneous coordinates used?
In standard Cartesian coordinates $(x, y)$, translation cannot be expressed as matrix multiplication because $x' = x + t_x$ is an addition. By introducing homogeneous coordinates $(x, y, 1)$, translation, rotation, and scaling can all be unified as matrix multiplications ($3 \times 3$ in 2D, $4 \times 4$ in 3D). This enables concatenation of multiple transformations into a single composite transformation matrix.

### 63. Explain the translation matrix.
In 2D homogeneous coordinates, the translation matrix $T(t_x, t_y)$ moves a point by displacement offsets $t_x$ and $t_y$:
$$T(t_x, t_y) = \begin{bmatrix} 1 & 0 & t_x \\ 0 & 1 & t_y \\ 0 & 0 & 1 \end{bmatrix}$$

### 64. What is the difference between scaling and shearing?
- **Scaling** alters the dimensions (size) of an object along coordinate axes by multiplying coordinates by scale factors ($s_x, s_y$). Uniform scaling preserves the object's proportions, while non-uniform scaling distorts proportions but keeps coordinate axes orthogonal.
- **Shearing** distorts the shape of an object such that parallel layers slide past one another along an axis by an amount proportional to their perpendicular distance, transforming rectangles into parallelograms.

### 65. What is the purpose of reflection?
Reflection produces a mirror image of an object across a specified reflection axis or plane (e.g., $X$-axis, $Y$-axis, origin, or line $y = x$). It is equivalent to a $180^\circ$ rotation out of the plane into 3D space, reversing vertex ordering (winding order).

### 66. Why is rotation about the origin?
Standard trigonometric rotation formulas ($x' = x\cos\theta - y\sin\theta$, $y' = x\sin\theta + y\cos\theta$) are derived based on polar coordinates referenced to the origin $(0, 0)$. Thus, standard rotation matrices rotate objects strictly about the coordinate origin.

### 67. How can rotation about an arbitrary point be achieved?
To rotate about an arbitrary pivot point $(x_r, y_r)$:
1. Translate the pivot point to the origin: $T(-x_r, -y_r)$
2. Apply rotation about the origin: $R(\theta)$
3. Translate the origin back to the pivot point: $T(x_r, y_r)$
$$M_{\text{composite}} = T(x_r, y_r) \cdot R(\theta) \cdot T(-x_r, -y_r)$$

### 68. What is the advantage of matrix representation?
1. Unified representation for all transformations using matrix multiplication.
2. Allows combining arbitrary sequences of transformations into a single composite matrix ($M_{\text{comp}} = M_n \dots M_1$).
3. Highly optimized hardware acceleration via modern GPUs.
4. Clean mathematical framework for coordinate spaces (object space, world space, eye space, clip space).

### 69. What is the order of matrix multiplication in transformations?
Matrix multiplication is **non-commutative** ($A \cdot B \neq B \cdot A$). When using column vector convention ($P' = M \cdot P$), matrices are multiplied from right to left in the order transformations are applied:
$$P' = (M_3 \cdot M_2 \cdot M_1) \cdot P$$
$M_1$ is applied first, followed by $M_2$, and then $M_3$.

### 70. Why is translation not represented by a $2 \times 2$ matrix?
A $2 \times 2$ matrix operation on a vector $[x, y]^T$ yields linear combinations:
$$\begin{bmatrix} a & b \\ c & d \end{bmatrix} \begin{bmatrix} x \\ y \end{bmatrix} = \begin{bmatrix} ax + by \\ cx + dy \end{bmatrix}$$
Since translation requires adding constant terms ($x + t_x, y + t_y$), it cannot map the origin to a non-zero position linearly in 2D. Adding a third homogeneous dimension makes translation a linear operation in 3D projective space.

### 71. What is the determinant of a rotation matrix?
The determinant of a valid 2D or 3D pure rotation matrix is always **$+1$** ($\det(R) = 1$). It is an orthogonal matrix ($R^T = R^{-1}$), which preserves vector lengths and angles (isometry). A reflection matrix has determinant **$-1$**.

### 72. Explain composite transformations.
A composite transformation is formed by combining multiple elementary transformations (translation, rotation, scaling) into a single overall transformation matrix by matrix multiplication. Applying the single precomputed composite matrix to thousands of vertices is vastly more efficient than applying each transformation individually.

### 73. What is an affine transformation?
An affine transformation is a transformation that preserves points, straight lines, and planes. Parallel lines remain parallel after an affine transformation, and ratios of lengths along parallel line segments are preserved. Affine transformations include translation, rotation, scaling, reflection, and shearing.

### 74. Give real-life applications of 2D transformations.
1. **Computer-Aided Design (CAD)**: Moving, scaling, and rotating architectural schematics.
2. **Video Games**: Character movement, sprite rotation, and camera viewport scrolling.
3. **Graphic Design Software (Photoshop/Illustrator)**: Object repositioning, resizing, skewing, and mirroring.
4. **Computer Vision & Robotics**: Robot arm inverse kinematics and camera image registration.

### 75. Compare 2D and 3D transformations.
| Feature | 2D Transformation | 3D Transformation |
| :--- | :--- | :--- |
| **Matrix Size (Homogeneous)** | $3 \times 3$ matrix | $4 \times 4$ matrix |
| **Point Vector** | $[x, y, 1]^T$ | $[x, y, z, 1]^T$ |
| **Rotation Axis** | Rotates about a point (perpendicular $Z$-axis) | Rotates about an axis ($X, Y, Z$ or arbitrary 3D line) |
| **Degrees of Freedom** | 3 (2 translation, 1 rotation) | 6 (3 translation, 3 rotation) |

---

## Solutions to Assignment Questions

### 33. Rotate a polygon about an arbitrary pivot point
$$M = T(x_r, y_r) \cdot R(\theta) \cdot T(-x_r, -y_r)$$
Implemented in Python:
```python
def rotate_about_pivot(points, xr, yr, theta_deg):
    rad = math.radians(theta_deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    T_neg = np.array([[1, 0, -xr], [0, 1, -yr], [0, 0, 1]])
    R     = np.array([[cos_a, -sin_a, 0], [sin_a, cos_a, 0], [0, 0, 1]])
    T_pos = np.array([[1, 0, xr], [0, 1, yr], [0, 0, 1]])
    M = T_pos @ R @ T_neg
    return [tuple((M @ np.array([x, y, 1.0]))[:2]) for x, y in points]
```

### 34. Perform non-uniform scaling
When scaling factors $s_x \neq s_y$, non-uniform scaling occurs:
$$S(s_x, s_y) = \begin{bmatrix} s_x & 0 & 0 \\ 0 & s_y & 0 \\ 0 & 0 & 1 \end{bmatrix}$$
Example: For $s_x = 2.0, s_y = 0.5$, an object becomes twice as wide and half as tall.

### 35. Implement reflection about the line $y = x$
The reflection matrix about the line $y = x$ swaps the coordinates $(x' = y, y' = x)$:
$$RF_{y=x} = \begin{bmatrix} 0 & 1 & 0 \\ 1 & 0 & 0 \\ 0 & 0 & 1 \end{bmatrix}$$

### 36. Create an interactive menu-driven transformation program
This was created in `Lab4/composite_transformation.py` allowing terminal and graphical interactive transformation pipeline execution.

### 37. Animate continuous rotation of an object
Achieved in OpenGL via GLUT's idle callback (`glutIdleFunc(idle)`):
```python
def idle():
    global angle
    angle = (angle + 1.0) % 360.0
    glutPostRedisplay()
```

### 38. Compare transformation matrices for 2D and 3D graphics
- 2D Translation: $3 \times 3$ with $t_x, t_y$ in 3rd column.
- 3D Translation: $4 \times 4$ with $t_x, t_y, t_z$ in 4th column.
- 2D Rotation: single angle $\theta$ in $Z$-plane.
- 3D Rotation: 3 Euler angle matrices ($R_x(\alpha), R_y(\beta), R_z(\gamma)$) or quaternions.

### 39. Implement all transformations using a single matrix multiplication function
```python
def apply_transformation_matrix(points, M_3x3):
    transformed = []
    for x, y in points:
        P = np.array([x, y, 1.0])
        P_prime = M_3x3 @ P
        transformed.append((P_prime[0], P_prime[1]))
    return transformed
```

### 40. Apply multiple transformations to a complex polygon
Matrix pipeline concatenation:
$$M_{\text{composite}} = M_n \cdot M_{n-1} \cdots M_2 \cdot M_1$$
Multiplies all transformation stages once into $M_{\text{composite}}$, then applies $M_{\text{composite}}$ to each vertex of the complex polygon.
