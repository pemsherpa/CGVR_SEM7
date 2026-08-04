import sys, pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

pygame.init()
W,H=1000,700
pygame.display.set_mode((W,H), DOUBLEBUF|OPENGL)
pygame.display.set_caption("Earth Demo")

glEnable(GL_DEPTH_TEST)
glEnable(GL_LIGHTING)
glEnable(GL_LIGHT0)
glLightfv(GL_LIGHT0, GL_POSITION, (5,5,5,1))
glLightfv(GL_LIGHT0, GL_DIFFUSE, (1,1,1,1))
glEnable(GL_COLOR_MATERIAL)
glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

gluPerspective(45,W/H,0.1,100)
quad=gluNewQuadric()
gluQuadricNormals(quad,GLU_SMOOTH)

rot=0
camz=-8
clock=pygame.time.Clock()

while True:
    for e in pygame.event.get():
        if e.type==QUIT:
            pygame.quit();sys.exit()
    k=pygame.key.get_pressed()
    if k[K_w]: camz+=0.1
    if k[K_s]: camz-=0.1

    rot+=0.4
    glClearColor(0.02,0.02,0.06,1)
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    glLoadIdentity()
    glTranslatef(0,0,camz)

    # stars
    glDisable(GL_LIGHTING)
    glPointSize(2)
    glBegin(GL_POINTS)
    glColor3f(1,1,1)
    for i in range(300):
        x=((i*37)%100-50)/5
        y=((i*71)%100-50)/5
        z=-20-((i*19)%30)
        glVertex3f(x,y,z)
    glEnd()
    glEnable(GL_LIGHTING)

    # sun
    glPushMatrix()
    glTranslatef(3.5,1.5,-3)
    glColor3f(1.0,0.85,0.2)
    gluSphere(quad,0.35,24,24)
    glPopMatrix()

    # earth
    glPushMatrix()
    glRotatef(rot,0,1,0)
    glColor3f(0.1,0.45,1.0)
    gluSphere(quad,1.3,64,64)

    # latitude lines
    glDisable(GL_LIGHTING)
    glColor3f(0.7,0.9,1)
    for lat in range(-60,61,30):
        glPushMatrix()
        glRotatef(lat,1,0,0)
        glut=False
        glBegin(GL_LINE_LOOP)
        import math
        r=1.3*math.cos(math.radians(lat))
        y=1.3*math.sin(math.radians(lat))
        for a in range(120):
            t=2*math.pi*a/120
            glVertex3f(r*math.cos(t),y,r*math.sin(t))
        glEnd()
        glPopMatrix()
    glEnable(GL_LIGHTING)
    glPopMatrix()

    pygame.display.flip()
    clock.tick(60)