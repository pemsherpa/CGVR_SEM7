# EXPERIMENT – 4: IMPLEMENT COMPOSITE TRANSFORMATIONS USING MATRIX REPRESENTATION

## Aim
To implement the fundamental two-dimensional geometric transformations using homogeneous coordinate representation and transformation matrices in OpenGL.

## Course Outcome
**CO2:** Apply two-dimensional graphics transformations using matrix representation and homogeneous coordinates for graphical object manipulation.

## Bloom's Taxonomy Level
**L3 – Apply**

## Learning Objectives
After completing this experiment, the student will be able to:
1. Understand coordinate transformations.
2. Apply matrix operations in computer graphics.
3. Implement translation, rotation, scaling, reflection, and shearing.
4. Understand homogeneous coordinates.
5. Develop OpenGL programs for geometric transformations.

---

## Theoretical Background & Mathematical Formulations

### 1. Homogeneous Coordinates
In 2D Euclidean space, a point is represented as $(x, y)$. However, translation cannot be expressed as a matrix multiplication in 2D space. By converting to **3D Homogeneous Coordinates**, every 2D point is represented as a 3x1 column vector:

$$\mathbf{P} = \begin{bmatrix} x \\ y \\ 1 \end{bmatrix}$$

All 2D geometric transformations can then be represented as **$3 \times 3$ matrices**. The transformed point $\mathbf{P}' = [x', y', 1]^T$ is computed via matrix-vector multiplication:

$$\mathbf{P}' = \mathbf{M} \cdot \mathbf{P}$$

---

### 2. Fundamental 3x3 Transformation Matrices

#### A. Translation Matrix $T(t_x, t_y)$
$$T(t_x, t_y) = \begin{bmatrix} 1 & 0 & t_x \\ 0 & 1 & t_y \\ 0 & 0 & 1 \end{bmatrix}$$

#### B. Rotation Matrix $R(\theta)$ (Counter-clockwise about origin)
$$R(\theta) = \begin{bmatrix} \cos\theta & -\sin\theta & 0 \\ \sin\theta & \cos\theta & 0 \\ 0 & 0 & 1 \end{bmatrix}$$

#### C. Scaling Matrix $S(s_x, s_y)$ (About origin)
$$S(s_x, s_y) = \begin{bmatrix} s_x & 0 & 0 \\ 0 & s_y & 0 \\ 0 & 0 & 1 \end{bmatrix}$$

#### D. Reflection Matrices $RF$
- **About X-axis ($y=0$):** 
  $$\begin{bmatrix} 1 & 0 & 0 \\ 0 & -1 & 0 \\ 0 & 0 & 1 \end{bmatrix}$$
- **About Y-axis ($x=0$):** 
  $$\begin{bmatrix} -1 & 0 & 0 \\ 0 & 1 & 0 \\ 0 & 0 & 1 \end{bmatrix}$$
- **About Origin:** 
  $$\begin{bmatrix} -1 & 0 & 0 \\ 0 & -1 & 0 \\ 0 & 0 & 1 \end{bmatrix}$$
- **About line $y = x$:** 
  $$\begin{bmatrix} 0 & 1 & 0 \\ 1 & 0 & 0 \\ 0 & 0 & 1 \end{bmatrix}$$
- **About line $y = -x$:** 
  $$\begin{bmatrix} 0 & -1 & 0 \\ -1 & 0 & 0 \\ 0 & 0 & 1 \end{bmatrix}$$

#### E. Shearing Matrix $SH(sh_x, sh_y)$
$$SH(sh_x, sh_y) = \begin{bmatrix} 1 & sh_x & 0 \\ sh_y & 1 & 0 \\ 0 & 0 & 1 \end{bmatrix}$$

---

### 3. Composite Transformations (Matrix Multiplication)

When a sequence of transformations is applied to an object, the individual matrices $M_1, M_2, \dots, M_n$ can be multiplied together to form a single **Composite Matrix** $M_{comp}$:

$$M_{comp} = M_n \cdot M_{n-1} \cdots M_2 \cdot M_1$$

#### A. Rotation about an Arbitrary Point $(x_r, y_r)$
To rotate an object about a pivot point $(x_r, y_r)$ instead of the origin:
1. Translate pivot to origin: $T(-x_r, -y_r)$
2. Rotate by $\theta$: $R(\theta)$
3. Translate origin back to pivot: $T(x_r, y_r)$

$$M_{comp} = T(x_r, y_r) \cdot R(\theta) \cdot T(-x_r, -y_r)$$

$$M_{comp} = \begin{bmatrix} 1 & 0 & x_r \\ 0 & 1 & y_r \\ 0 & 0 & 1 \end{bmatrix} \begin{bmatrix} \cos\theta & -\sin\theta & 0 \\ \sin\theta & \cos\theta & 0 \\ 0 & 0 & 1 \end{bmatrix} \begin{bmatrix} 1 & 0 & -x_r \\ 0 & 1 & -y_r \\ 0 & 0 & 1 \end{bmatrix}$$

#### B. Scaling about an Arbitrary Point $(x_f, y_f)$
To scale an object relative to a fixed point $(x_f, y_f)$:
1. Translate fixed point to origin: $T(-x_f, -y_f)$
2. Scale by $(s_x, s_y)$: $S(s_x, s_y)$
3. Translate origin back to fixed point: $T(x_f, y_f)$

$$M_{comp} = T(x_f, y_f) \cdot S(s_x, s_y) \cdot T(-x_f, -y_f)$$

---

## File Structure & Code Execution

- **Implementation Code**: [composite_transformation.py](file:///Users/pemasherpa/Desktop/Everything/RVU/CGVR/Lab4/composite_transformation.py)

### How to Run

```bash
python3 Lab4/composite_transformation.py
```

### User Interaction Steps:
1. Select 2D Object:
   - 1: Point
   - 2: Line Segment
   - 3: Triangle
   - 4: Rectangle
   - 5: House Shape Polygon
2. Select Transformation:
   - Fundamental: Translation, Rotation, Scaling, Reflection, Shearing
   - Composite: Rotation about arbitrary point, Scaling about arbitrary point, Custom Pipeline Concatenation.
3. Observe output:
   - Console displays step-by-step matrix operations, homogeneous composite matrix, and original vs transformed coordinate values.
   - OpenGL window displays grid lines, original object in BLUE, transformed object in RED, and overlayed 3x3 homogeneous transformation matrix.
