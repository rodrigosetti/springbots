"""
This module contains the core part of the sprinbots, which is their nodes
and springs. Here are implemented all the physics behaviour and interations
among those parts.
"""

# Get all math we need
from math import *

# Get vector
from vector import Vector

#
# Constants
#

#: The rate which the angle changes, this parameter
#: affects the frequency of motion of springs
ANGLE_STEP = 0.025

#: Acceleration vector aplied every step of simulation on nodes
GRAVITY = (0,0.3)

#: % of node's velocity lost every step of simulation
AIR_RESISTANCE = 0.01

#: Parameter which determines the force of springs
ELASTICITY = 0.6

#: Causes buoyancy force on springs motion
VISCOSITY = 0.05

#: This parameter is not used on physics
NODE_WEIGHT = 1.26

#: Node's radius
RADIUS = 8

#: Direction constant: UP
UP              = 1

#: Direction constant: DOWN
DOWN    = 2

#: Direction constant: LEFT
LEFT    = 3

#: Direction constant: RIGHT
RIGHT   = 4

class Node(object):
    """
    A node is a mass circle which acts gravity, air resistance. It has a
    position and a velocity and can be connected by springs
    """

    def __init__(self, pos=(0,0), vel=(0,0), acc=(0,0), id=0):
        """
        Creates a node with a start position, velocity and acceleration
        """
        self.pos = Vector(pos[0], pos[1])
        self.vel = Vector(vel[0], vel[1])
        self.acc = Vector(acc[0], acc[1])
        self.id = id

    def refresh(self, atr=AIR_RESISTANCE, grav=GRAVITY, elast=ELASTICITY):
        """
        Refreshes node: changes position based on velocity and velocity based
        on acceleration. Also applies gravity and air resistance
        """
        self.pos = self.pos + self.vel
        self.vel = self.vel + (self.acc * elast)
        self.pos = self.pos + (self.acc * (1.0 - elast))
        self.acc = Vector(0,0)

        self.vel = self.vel + Vector(grav[0], grav[1])
        self.vel = self.vel * (1.0 - atr)

    def colideWall(self, limit, side, atr_normal=0.6, atr_surface=0.5, min_vel=0.99, radius=RADIUS):
        """
        Colides this node with a wall, if possible. Applies surface friction and changes velocity
        """
        global UP, DOWN, LEFT, RIGHT

        if side == LEFT and self.pos.x < limit + radius:
            self.pos.x = limit + radius
            self.vel.x = self.vel.x * - atr_normal if abs(self.vel.x * - atr_normal) > min_vel else 0.0
            self.vel.y *= atr_surface
        elif side == RIGHT and self.pos.x > limit - radius:
            self.pos.x = limit - radius
            self.vel.x = self.vel.x * - atr_normal if abs(self.vel.x * - atr_normal) > min_vel else 0.0
            self.vel.y *= atr_surface
        if side == UP and self.pos.y < limit + radius:
            self.pos.y = limit + radius
            self.vel.x *= atr_surface
            self.vel.y = self.vel.y * - atr_normal if abs(self.vel.y * - atr_normal) > min_vel else 0.0
        elif side == DOWN and self.pos.y > limit - radius:
            self.pos.y = limit - radius
            self.vel.x *= atr_surface
            self.vel.y = self.vel.y * - atr_normal if abs(self.vel.y * - atr_normal) > min_vel else 0.0
        elif side not in [UP, LEFT, RIGHT, DOWN]:
            raise ValueError("side must be UP, LEFT, RIGHT or DOWN.")

    def colide(self, other, radius=RADIUS):
        """
        Colides this node with another one, if possible
        """
        # Nao pode colidir consigo proprio
        if (self is other):
            return

        # calcula distancia entre os bots
        distancia = (self.pos - other.pos).length()

        # detecta colisao
        if distancia != 0 and distancia <= radius*2:
            colisao = (self.pos - other.pos)        # vetor colisao(ligando os dois)

            # projeta velocidades no vetor colisao
            trans_a = self.vel.projection(colisao)
            trans_b = other.vel.projection(colisao)

            # corrige posicoes
            r = (colisao.unit() * radius * 2) - colisao
            self.pos += r / 2.0
            other.pos -= r / 2.0

            # troca velocidades
            self.vel += trans_b - trans_a
            other.vel += trans_a - trans_b

    def __repr__(self):
        return "<Node pos=%dx%d, vel=%.2fx%.2f>" % (self.pos.x, self.pos.y, self.vel.x, self.vel.y)



class Spring(object):
    """
    Spring: An object that connect nodes, and can only exist if connecting two
    diferent nodes. A spring has a normal lenght state and if pulled or pushed
    it applies a force on the nodes it connects to restabilish it's state.
    Springs can also move like muscles by changing it normal lenght by a sine
    wave frequency.
    """

    def __init__(self, a, b, amplitude=0, offset=pi, normal=None):
        """
        Creates a spring connecting nodes A and B, with an start amplitude, offset and
        normal lenght.
        """
        self.a = a
        self.b = b
        self.normal = sqrt(sum((a.pos-b.pos)**2)) if normal is None else normal
        self.amplitude = amplitude
        self.offset = offset

    def refresh(self, elast=0.5, ang=None, visc=0):
        """
        Refreshes a spring by appling forces on surrounding nodes and creating
        buoyancy forces if there are viscosity on the enviroment.
        """
        ampl = 0 if ang is None else self.amplitude
        if ang is None:
            ang = 0

        delta = (self.a.pos + self.a.vel) - (self.b.pos + self.b.vel)
        dist = sqrt(sum(delta**2))
        N = self.normal + (sin(ang+self.offset) * ampl * self.normal)

        if dist != 0:
            self.a.acc += (delta/dist * (N-dist) * (1.0-elast) * 0.5)
            self.b.acc -= (delta/dist * (N-dist) * (1.0-elast) * 0.5)

        # Aplica empuxo de fluido
        if visc > 0:
            vnormal = (self.a.pos - self.b.pos).perpendicular()
            if vnormal.length() > 0:
                vnodes = self.a.vel + self.b.vel
                vproj = -vnodes.projection(vnormal)
                accel = vproj * log((self.a.pos - self.b.pos).length(), 10) * visc

                self.a.acc += accel
                self.b.acc += accel

    def __repr__(self):
        return "<Spring normal=%.2f, amplitude=%.2f>" % (self.normal, self.amplitude)
