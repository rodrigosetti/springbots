from springbot import Springbot
from gear import *

# Importa random para mutacao e geracao randomica de springbot
import random
from latimname import latimname

# Importa rotinas matematicas
from math import sqrt, pi

# Vetor
from vector import Vector

import copy

#
# Globals
#

#: Keep track of the bloodline id being generated
_bloodline_count = 0

#: Separator string between bloodline ids in Springbot's bloodline field
BLOODLINE_SEP = ':'

#
# Springbot evoluivel
#
class EvolveSpringbot(Springbot):
    """
    Extends springbot to evolution methods
    """

    def __init__(self, parent=None, name="Unnamed", startangle=0, random=False):

        global _bloodline_count

        if random:
            super(EvolveSpringbot, self).__init__(parent=random_springbot())
        else:
            super(EvolveSpringbot, self).__init__(parent, name, startangle)

        if not parent:
            self['fitness'] = 0
            self['bloodline'] = hex(_bloodline_count)[2:] + BLOODLINE_SEP

        self._bloodline_count = 0
        _bloodline_count += 1

    def generations(self):
        """
        Return generations number
        """
        return len(self['bloodline'].split(BLOODLINE_SEP)) - 1

    def addBloodline(self, parent):
        """
        Adds a bloodline id
        """
        self['bloodline'] += hex(parent._bloodline_count)[2:] + BLOODLINE_SEP
        parent._bloodline_count += 1

    def crossover(self, other):
        """
        Crosses this springbot with another one, returning a new one
        """
        global _bloodline_count

        # Create new springbot
        breed = EvolveSpringbot()

        # Breed springbots info
        for key in self:
            breed[key] = self[key]

        breed['fitness'] = 0
        breed['name'] = ' '.join(set(self['name'].split() + other['name'].split()))
        breed['adapted'] = "random"

        # Set bloodline
        try:
            breed['bloodline'] += 'X' + \
                other['bloodline'].split(BLOODLINE_SEP)[0] + '...' + other['bloodline'].split(BLOODLINE_SEP)[-2] + \
                BLOODLINE_SEP
        except KeyError:
            pass

        # For each spring in self and other
        for springA, springB in zip(self.springs + ([None] * ((len(other.springs)-len(self.springs))/2)),
                                    other.springs + ([None] * ((len(self.springs)-len(other.springs))/2))):

            if springA is None: springA = springB
            elif springB is None: springB = springA

            # Select spring
            spring = random.choice([springA,springB])

            # Select node A
            nodeA = breed.getNode(spring.a.id)
            if nodeA is None:
                nodeA = random.choice([self,other]).getNode(spring.a.id)
                if nodeA is None: nodeA = spring.a

                # Create node A
                new_nodeA = Node(nodeA.pos, nodeA.vel, nodeA.acc)
                new_nodeA.id = nodeA.id
                nodeA = new_nodeA

                # Add node A
                breed.add(nodeA)

            # Select node B
            nodeB = breed.getNode(spring.b.id)
            if nodeB is None:
                nodeB = random.choice([self,other]).getNode(spring.b.id)
                if nodeB is None: nodeB = spring.b

                # Create node B
                new_nodeB = Node(nodeB.pos, nodeB.vel, nodeB.acc)
                new_nodeB.id = nodeB.id
                nodeB = new_nodeB

                # Add node B
                breed.add(nodeB)

            # Add created spring
            breed.add(Spring(nodeA, nodeB, spring.amplitude,
                             spring.offset, spring.normal))

        # Remove unconnected elements
        breed.removeUnconnected()

        # Return new
        return breed

    def mutate(self, newnodedist=100, nodevariation=10):
        """
        Mutates a random structure of the springbot, which may be
        adding or removing a node, adding or removing a spring,
        changing any spring's parameter or changing a node position.
        """
        # Tipos de mutacao:
        # 0 - Adicao de node
        # 1 - Remocao de node(se N > 1 e permanece conexo)
        # 2 - Adicao de spring(se nao eh totalmente conexo)
        # 3 - Remocao de spring(se permanece conexo)
        # 4 - altera propriedades do spring
        # 5 - muda posicao de node(e estica springs)

        if len(self.nodes) == 0:
            return

        # Sorteia
        tipo = random.choice(range(6))

        if tipo == 0: # 0 - Adicao de node
            neigh = random.choice(self.nodes)
            newnode = Node(pos=(neigh.pos.x + random.uniform(-newnodedist, newnodedist),
                            neigh.pos.y + random.uniform(-newnodedist, newnodedist)))

            self.add(newnode)       # Adiciona novo node
            self.add(Spring(neigh, newnode, offset=random.uniform(0,pi*2))) # Adiciona nova spring

        elif tipo == 1 and len(self.nodes) > 1: # 1 - Remocao de node(se N > 1 e permanece conexo)

            # Cria uma copia do springbot
            copia = Springbot()
            copia.nodes = copy.copy(self.nodes)
            copia.springs = copy.copy(self.springs)

            # Escolhe um node para remover
            toremove = random.choice(copia.nodes)

            # Testa remocao na copia
            copia.remove(toremove)
            if not copia.unconnected():
                # OK, Continua conexo: pode remover do atual
                for node in self.nodes:
                    if node.id == toremove.id:
                        self.remove(node)
                        break

        elif tipo == 2 and len(self.nodes) > 1: # 2 - Adicao de spring(se nao eh totalmente conexo)
            a = random.choice(self.nodes)
            b = random.choice(self.nodes)

            # Verifica se nao eh o mesmo
            while a is b:
                b = random.choice(self.nodes)

            self.add(Spring(a, b, offset=random.uniform(0,pi*2)))   # Adiciona nova spring
        elif tipo == 3 and len(self.springs) > 0: # 3 - Remocao de spring(se permanece conexo)

            # Escolhe spring
            toremove = random.choice(self.springs)

            # Remove
            self.remove(toremove)
            if self.unconnected():
                # Opa, nao eh mais conexo, volta atras:
                self.add(toremove)

        elif tipo == 4 and len(self.springs) > 0: # 4 - altera propriedades do spring
            spring = random.choice(self.springs)
            if random.choice([1, 2]) == 1:
                spring.offset = max(spring.offset + random.uniform(-pi, pi), 0)
            else:
                added = random.uniform(-0.5, 0.5)
                spring.amplitude = spring.amplitude + added if abs(spring.amplitude + added) <= 0.5 else spring.amplitude

        elif tipo == 5: # 5 - muda posicao de node(e estica springs)
            node = random.choice(self.nodes)
            node.pos.x += random.uniform(-nodevariation,nodevariation)
            node.pos.y += random.uniform(-nodevariation,nodevariation)

            # Corrige springs
            for spring in self.springs:
                if spring.a is node or spring.b is node:
                    spring.normal = sqrt(sum((spring.a.pos-spring.b.pos)**2))

        # Returns itself
        return self

#                                                                              #
################################################################################
#                                                                              #

def random_springbot(nodes_num=10, springs_num=30, noderadius=100):
    """
    Creates a new springbot totally random
    """
    # Creates a new springbot
    springbot = EvolveSpringbot(name=latimname(5))
    springbot["adapted"] = "random"

    for x in xrange(random.randint(nodes_num/2, nodes_num)):
        # Adiciona um node
        newnode = Node(pos=(random.uniform(-noderadius, noderadius),
                random.uniform(-noderadius, noderadius)))
        springbot.add(newnode)  # Adiciona novo node

    if len(springbot.nodes) > 1:
        for x in xrange(random.randint(springs_num/2, springs_num)):
            # Adiciona uma spring aleatoria
            a = random.choice(springbot.nodes)
            b = random.choice(springbot.nodes)

            # Verifica se nao eh o mesmo
            while a is b:
                b = random.choice(springbot.nodes)

            # Adiciona nova spring
            springbot.add(Spring(a, b, offset=random.uniform(0,pi*2), amplitude=random.uniform(-0.5, 0.5)))

    # Remove unconnected elements
    springbot.removeUnconnected()

    return springbot

#                                                                              #
################################################################################
#                                                                              #
