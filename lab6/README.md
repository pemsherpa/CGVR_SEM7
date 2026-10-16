# EXPERIMENT – 6: IMPLEMENT THE Z-BUFFER ALGORITHM FOR HIDDEN SURFACE REMOVAL

## Aim
To implement the **Z-Buffer (Depth-Buffer) algorithm for hidden surface removal** using OpenGL, demonstrating depth comparison, visible surface determination, and resolving overlapping and intersecting 3D surfaces.

## Course Outcome
**CO3:** Apply 3D graphics concepts and visible surface detection algorithms (Z-Buffer / Depth Buffer) for realistic object rendering and hidden surface removal.

## Bloom's Taxonomy Level
**L3 – Apply**

## Learning Objectives
After completing this experiment, the student will be able to:
1. Understand the concept of **hidden surface removal** (visible surface detection) in 3D computer graphics.
2. Differentiate between **Object-Space** (e.g., Painter's algorithm, Roberts algorithm) and **Image-Space** (e.g., Z-Buffer, Scanline, Area subdivision) methods.
3. Understand the mathematical foundation of plane equations ($Ax + By + Cz + D = 0$) and **incremental scanline depth calculation** ($\Delta z = -A/C$).
4. Understand the data structures: **Frame Buffer (Color Buffer)** and **Depth Buffer (Z-Buffer)**.
5. Implement and observe the difference between rendering scenes with **Z-Buffer enabled vs disabled**.
6. Develop OpenGL programs utilizing `GL_DEPTH_TEST`, `glDepthFunc`, and `glClear(GL_DEPTH_BUFFER_BIT)`.

---

## Theoretical Background & Mathematical Formulations

### 1. The Hidden Surface Removal Problem
When three-dimensional objects are projected onto a two-dimensional viewing plane (screen), multiple surfaces may map to the same pixel $(x, y)$. To render scenes realistically, the surfaces that are obscured by other opaque surfaces closer to the observer must be identified and eliminated.

Visible surface detection methods are classified into two broad categories:
- **Object-Space Methods:** Compare objects/polygons directly in 3D world space (e.g., Back-Face Culling, Painter's Algorithm). Complexity is typically $O(N^2)$ where $N$ is the number of polygons.
- **Image-Space Methods:** Determine visibility on a point-by-point basis at each pixel position on the projection plane (e.g., Z-Buffer algorithm). Complexity is $O(N \times \text{number of pixels})$.

---

### 2. The Z-Buffer (Depth-Buffer) Algorithm
The Z-Buffer algorithm is an **image-space** algorithm developed by Edwin Catmull in 1974. It operates by maintaining two parallel 2D buffers having dimensions equal to the screen resolution $(W \times H)$:

1. **Frame Buffer / Color Buffer `frame_buffer[x, y]`:**
   - Stores the color value $(R, G, B)$ of the visible surface currently mapped to pixel $(x, y)$.
2. **Depth Buffer / Z-Buffer `depth_buffer[x, y]`:**
   - Stores the closest depth ($z$-coordinate) encountered so far for pixel $(x, y)$.

---

### 3. Mathematical Formulations & Derivations

#### A. Plane Equation
A planar polygon surface in 3D space is defined by the linear equation:
$$A \cdot x + B \cdot y + C \cdot z + D = 0$$

Where $(A, B, C)$ represents the normal vector to the plane surface.

Solving for depth $z$ at any point $(x, y)$:
$$z = \frac{-A \cdot x - B \cdot y - D}{C} \quad (C \neq 0)$$

#### B. Incremental Scanline Depth Calculation
Evaluating the full plane equation for every pixel is computationally expensive. Because pixels along a horizontal scanline are processed sequentially, we can calculate depth incrementally:

At pixel $(x, y)$:
$$z_1 = \frac{-A \cdot x - B \cdot y - D}{C}$$

At the adjacent horizontal pixel $(x + 1, y)$:
$$z_2 = \frac{-A(x + 1) - B \cdot y - D}{C} = \frac{-A \cdot x - B \cdot y - D}{C} - \frac{A}{C} = z_1 - \frac{A}{C}$$

Thus, along any horizontal scanline:
$$\Delta z = -\frac{A}{C}$$

> [!TIP]
> Each subsequent pixel along a scanline requires only **one subtraction operation**, drastically optimizing rasterization performance.

Similarly, when moving between successive scanlines (vertical step from $y$ to $y - 1$):
$$\Delta z_{\text{scan}} = \frac{B}{C}$$

---

### 4. Algorithm Flow & Pseudo-Code

```text
Algorithm: Z-Buffer Hidden Surface Removal
----------------------------------------------------------------------
1. Initialize Buffers:
     For each pixel (x, y) on the screen:
         depth_buffer[x, y] = 1.0          // Maximum depth (far clipping plane)
         frame_buffer[x, y] = BACKGROUND_COLOR

2. Process Polygons:
     For each polygon P in the scene:
         For each pixel (x, y) covered by the projection of P:
             Calculate depth z(x, y) of polygon P at pixel (x, y)
             
             // Depth Test:
             If z(x, y) < depth_buffer[x, y]:  // Current surface is closer
                 depth_buffer[x, y] = z(x, y)   // Update closest depth
                 frame_buffer[x, y] = Color(P)  // Update pixel color

3. Display:
     Output the contents of frame_buffer to the screen display.
```

---

### 5. Comparison: Z-Buffer vs Painter's Algorithm

| Feature | Painter's Algorithm (Depth Sort) | Z-Buffer Algorithm (Depth Buffer) |
| :--- | :--- | :--- |
| **Domain** | Object-Space | Image-Space |
| **Ordering Requirement** | Requires strictly sorting all polygons from back to front ($O(N \log N)$ or $O(N^2)$) | Independent of polygon rendering order |
| **Cyclic Overlap ($A \to B \to C \to A$)** | **Fails** (requires splitting polygons) | **Works correctly** per-pixel |
| **Intersecting Polygons** | **Fails** (cannot sort without polygon subdivision) | **Works correctly** at point of intersection |
| **Memory Requirement** | Low (only frame buffer) | Additional memory required for Depth Buffer |
| **Hardware Support** | Software only | Standard in all modern GPUs via OpenGL / DirectX |

---

## Implementation Details

The implementation is located in [z_buffer.py](file:///Users/pemasherpa/Desktop/Everything/RVU/CGVR/CGVR_SEM7/lab6/z_buffer.py) and features four interactive demonstration modes:

### 1. Scene 1: Overlapping Polygons at Distinct Depths
- Three colored planar polygons positioned at:
  - Red: $z = -2.0$ (Closest)
  - Green: $z = -3.5$ (Middle)
  - Blue: $z = -5.0$ (Farthest)
- **Observation:** When Z-Buffer is enabled, Red is always on top regardless of whether polygons are drawn front-to-back or back-to-front. When Z-Buffer is disabled, the last-drawn polygon overwrites earlier ones.

### 2. Scene 2: Intersecting 3D Surfaces
- Two intersecting 3D planes passing through each other.
- **Observation:** Demonstrates where Painter's algorithm fails, while Z-Buffer cleanly cuts the intersection line at pixel precision.

### 3. Scene 3: 3D Rotating Solid Objects (Cube & Pyramid)
- A 3D Cube and 3D Pyramid with distinct face colors.
- **Observation:** Turning Z-Buffer OFF causes back faces to bleed through and draw on top of front faces during rotation.

### 4. Scene 4: Discrete Software Z-Buffer Simulation
- Visualizes a $10 \times 10$ raster grid directly on-screen:
  - **Left Grid (Frame Buffer):** Displays the pixel colors assigned to each cell.
  - **Right Grid (Z-Buffer):** Displays the numerical floating-point depth values ($z = 0.35, 0.70, 1.00$) stored in each cell.

---

## File Structure & How to Run

```
CGVR_SEM7/
├── lab6/
│   ├── z_buffer.py     # Main OpenGL + GLUT implementation
│   └── README.md       # Lab documentation & theory
```

### Execution Command

```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Run Experiment 6
python lab6/z_buffer.py
```

### Interactive Keyboard & Mouse Controls

| Key / Input | Action |
| :--- | :--- |
| **`Z`** | **Toggle Z-Buffer (Depth Test) ON / OFF** |
| **`1` - `4`** | Select Demonstration Scene (1: Overlapping, 2: Intersecting, 3: Solids, 4: Pixel Grid) |
| **`O`** | Toggle Polygon Draw Order (Back-to-Front vs Front-to-Back) |
| **`D`** | Toggle Depth Map Visualizer (Grayscale Depth view) |
| **`Space`** | Toggle Automatic 3D Rotation |
| **Arrow Keys / Mouse Drag** | Rotate Scene freely in 3D |
| **`+` / `-`** | Zoom In / Zoom Out |
| **`R`** | Reset Camera and Rotation to default |
| **`H`** | Toggle On-Screen Heads-Up Display (HUD) |
| **`Q` / `ESC`** | Quit Application |
