"""
This modules implements the springbot, a creature builded with
spring and nodes.
"""

# Importa sys para escrever na saida padrao
import sys

# Rotinas para manuseamento de XML
import xml.dom.minidom
from xml.parsers.expat import ExpatError
import exceptions

# Importa as partes integrantes dos springbots
from gear import *

from math import sqrt, pi

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False

#
# Springbot class
#
class Springbot(object):
    """
    Springbot: Creature builded with nodes, which are masses, connected by
    springs which act like links between nodes pulling them together.
    Springs may also behave in a cicle muscle pulling and pushing the nodes it
    connects giving the creature some movement.
    """

    def __init__(self, parent=None, name="Unnamed", startangle=0):
        """
        Creates a brand new creature or a descendent from a parent
        """

        self.nodes = []
        self.springs = []
        self._node_count_id = 0

        if not parent:
            self._info = {"name": name, "angle": startangle}
        else:
            # Adiciona nodes
            for node in parent.nodes:
                newnode = Node((node.pos.x, node.pos.y))
                newnode.id = node.id
                self.add(newnode)

            # Adiciona springs
            for spring in parent.springs:
                # Determina referencia do spring
                for node in self.nodes:
                    if node.id == spring.a.id:
                        A = node
                for node in self.nodes:
                    if node.id == spring.b.id:
                        B = node
                self.add(Spring(A, B, spring.amplitude, spring.offset, spring.normal))

            # copia outros atributos
            self._node_count_id = parent._node_count_id
            self._info = dict(parent._info)

    def __getitem__(self, key):
        """
        Gets an info inten like a dictionary
        """
        return self._info[key]

    def __setitem__(self, key, value):
        """
        Gets an info inten like a dictionary
        """
        self._info[key] = value
        return value

    def refresh(self, atr=AIR_RESISTANCE, grav=GRAVITY, elast=ELASTICITY, visc=0, moving=True):
        """
        Refreshes creature's state
        """
        for node in self.nodes:
            node.refresh(atr, grav, elast)

        for spring in self.springs:
            spring.refresh(elast, self['angle'] if moving else None, visc)

        if moving:
            self['angle'] += ANGLE_STEP

    def loadXML(self, file=sys.stdin):
        """
        Reads a xml into this springbot
        """
        self.__init__(load_xml(file, limit=1)[0])
        return self

    def storeXML(self, file=sys.stdout):
        """
        Store this springbot into a xml file
        """
        store_xml([self], file)

    def colide(self, other, radius=RADIUS):
        """
        Colides this springbot to another
        """
        for node in self.nodes:
            for node2 in other.nodes:
                node.colide(node2, radius)

    def colideWall(self, limit, side, atr_normal=0.6, atr_surface=0.5, min_vel=0.99, radius=RADIUS):
        """
        Colides this springbot with a straigt wall
        """
        for node in self.nodes:
            node.colideWall(limit, side, atr_normal, atr_surface, min_vel, radius)

    def __len__(self):
        """
        Lenght(number of nodes)
        """
        return len(self.nodes)

    def add(self, objeto):
        """
        Adds an object: node or spring
        """
        if objeto.__class__ == Node:
            objeto.parent = self

            if not hasattr(objeto, "id"):
                self._node_count_id += 1
                objeto.id = self._node_count_id

            self.nodes.append(objeto)

        elif objeto.__class__ == Spring:

            # Verifica se ja nao existe uma spring entre esses nodes
            for spring in self.springs:
                if (spring.a is objeto.a or spring.b is objeto.a) and (spring.a is objeto.b or spring.b is objeto.b):
                    break
            else:
                objeto.parent = self
                self.springs.append(objeto)

    def remove(self, objeto):
        """
        Remove an object: node or spring
        """
        if objeto.__class__ == Node:
            # Verifica quais springs referenciam este objeto, e as deleta tambem
            removelist = set()
            for spring in self.springs:
                if spring.a is objeto or spring.b is objeto:
                    removelist.add(spring)
            for spring in removelist:
                self.springs.remove(spring)
            self.nodes.remove(objeto)

        elif objeto.__class__ == Spring:
            self.springs.remove(objeto)

    def massCenter(self):
        """
        Calculates the center of mass
        """
        cx, cy = 0, 0
        total = 0
        for node in self.nodes:
            total += 1
            cx += node.pos.x
            cy += node.pos.y

        return cx / total,      cy / total

    def boundingBox(self, radius=RADIUS):
        """
        Calculates its bounding box limits
        """
        if len(self.nodes) == 0:
            return 0, 0, 0, 0

        min_x, max_x = self.nodes[0].pos.x, self.nodes[0].pos.x
        min_y, max_y = self.nodes[0].pos.y, self.nodes[0].pos.y

        for node in self.nodes:
            min_x = min(min_x, node.pos.x)
            min_y = min(min_y, node.pos.y)
            max_x = max(max_x, node.pos.x)
            max_y = max(max_y, node.pos.y)

        return min_x-radius, min_y-radius, max_x+radius, max_y+radius

    def unconnected(self):
        """
        Gets all unconnected nodes
        """
        # Testa caso trivial
        if len(self.nodes) == 0:
            return []

        allsprings = self.springs[:]
        atualsprings = []

        allnodes = self.nodes[1:]
        atualnodes = [self.nodes[0]] # Inicia atualnodes com um elemento

        while len(atualnodes) > 0:
            atual = atualnodes.pop()

            # Seleciona todas springs que ligam ao node
            for spring in allsprings:
                if spring.a is atual or spring.b is atual:
                    atualsprings.append(spring)

            # Remove do allsprings todas as springs que estao no atual e
            # adiciona ao atualnodes todos os nodes ligados por essas springs
            for spring in atualsprings:
                allsprings.remove(spring)
                if spring.a in allnodes:
                    allnodes.remove(spring.a)
                    atualnodes.append(spring.a)
                elif spring.b in allnodes:
                    allnodes.remove(spring.b)
                    atualnodes.append(spring.b)

            # Zera atualsprings
            atualsprings = []

        # Se resta algum node em allnode, entao o springbot eh desconexo
        return allnodes

    def __repr__(self):
        return "<Springbot %s: %d nodes, %d springs>" % (self['name'], len(self.nodes), len(self.springs))

    def centerGround(self, height):
        """
        Center springbot width and touch ground
        """
        # Selects springbot's bouding box
        x1, y1, x2, y2 = self.boundingBox()

        # Calculates horizontal center offset
        cx = - ((x2+x1)/2)

        # Moves springbot to touch the ground under it
        # and moves sprinng bot to width center
        for node in self.nodes:
            node.pos.y -= (y2 - height) + RADIUS
            node.pos.x += cx

        return self


    def draw(self, screen, ticks=None, track_x=False, track_y=False,
            backgroundcolor=(20,10,0), showText=True, extrainfo=None):
        """
        Draws Springbot using pygame engine.
        Use this function to show the springbot
        """
        if not HAS_PYGAME:
            raise exceptions.NotImplementedError("No pygame module found")

        width, height = screen.get_size()


        # Gets the position center
        x1, y1, x2, y2 = self.boundingBox()

        zm = min(min(width/((x2-x1)+50.0), height/((y2-y1)+50.0)), 1.0)

        if track_x:
            cxp = (x2+x1)/2
            cx = cxp*zm - (width/2)
        else:
            cxp = cx = -width/2

        if track_y:
            cyp = (y2+y1)/2
            cy = cyp*zm - (height/2)
        else:
            cyp = cy = 0


        if showText:
            # Create Font
            font = pygame.font.Font(None, 20)

        # limpa tela
        screen.fill((0,0,0))

        siz_x, siz_y = width/10, height/10
        for x in xrange(0,width+100,siz_x):
            for y in xrange(0,height+100,siz_y):
                pygame.draw.rect(screen, backgroundcolor, 
                                 (((x - cxp) % (width+siz_x) - siz_x, (y - cyp) % (height+siz_y) - siz_y),
                                  (siz_x-10,siz_y-10)))

        # Desenha springs
        for spring in self.springs:
            length = (spring.a.pos - spring.b.pos).length()
            fator = (length - spring.normal)/length

            if fator <= 0:
                color = (255, 255-min(-fator * 255, 255), 255-min(-fator * 255, 255))
            elif fator > 0:
                color = (255-min(fator * 255, 255), 255, 255-min(fator * 255, 255))

            pygame.draw.line(screen, color, (spring.a.pos.x*zm - cx, spring.a.pos.y*zm - cy),
                    (spring.b.pos.x*zm - cx, spring.b.pos.y*zm - cy), int(3*zm))

        # Desenha nodes
        velx, vely = 0, 0
        for node in self.nodes:
            velx += node.vel.x
            vely += node.vel.y

            pygame.draw.circle(screen, (0,0,0), (int(node.pos.x*zm - cx), int(node.pos.y*zm - cy)), int(RADIUS*zm), 0)
            pygame.draw.circle(screen, (10,255,255), (int(node.pos.x*zm - cx), int(node.pos.y*zm - cy)), 
                               int(RADIUS*zm), int(2*zm))

        velx /= len(self.nodes)
        vely /= len(self.nodes)

        if showText:
            # Render springbot's name and info
            nametext = font.render("%s%s" % (self['name'], ": " + extrainfo if extrainfo else "."), False, (255,255,255))
            speedtext = font.render("speed: %.2f m/c" % (sqrt(velx**2 + vely**2)), False, (255,255,255))

            screen.blit(nametext, (5,5))
            screen.blit(speedtext, (5,20))

            if ticks:
                tickstext = font.render("clock: %d c" % (ticks), False, (255,255,255))
                screen.blit(tickstext, (5,35))


#                                                                             #
# ########################################################################### #
#                                                                             #

def store_xml(springbots, outfile=sys.stdout):
    """
    Writes a set os springbots into a xml
    """
    closeoutfile = (type(outfile) is str)
    if closeoutfile:
        outfile = open(outfile, 'w')

    outfile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    outfile.write('<!DOCTYPE springbots SYSTEM "http://springbots.sourceforge.net/springbots.dtd">\n')
    outfile.write('<springbots>\n')

    for n, springbot in enumerate(springbots):
        x1, y1, x2, y2 = springbot.boundingBox()
        cx, cy = (x1+x2)/2, (y1+y1)/2

        outfile.write('\t<springbot ')

        for key, value in springbot._info.iteritems():
            outfile.write('%s="%s" ' % (key, str(value)))

        outfile.write('>\n')

        for node in springbot.nodes:
            outfile.write('\t\t<node pos="%d,%d" id="S%dN%d" />\n' % (node.pos.x-cx, node.pos.y-cy, n, node.id))

        for spring in springbot.springs:
            outfile.write('\t\t<spring from="S%dN%d" to="S%dN%d" ' % (n, spring.a.id, n, spring.b.id))
            if round(spring.amplitude, 2) != 0:
                outfile.write('offset="%.3f" amplitude="%.3f" ' % (spring.offset, spring.amplitude))
            if fabs(spring.normal - sqrt(sum((spring.a.pos - spring.b.pos)**2))) > 1:
                outfile.write('normal="%.3f" ' % (spring.normal))
            outfile.write('/>\n')

        outfile.write("\t</springbot>\n")

    outfile.write("</springbots>\n")

    if closeoutfile:
        outfile.close()
    else:
        outfile.flush()

# ############################################################################ #

def isfloat(s):
    """
    Tests if a string is representing a float
    """
    if s.isdigit() or s == '.': return False
    spl = s.split('.')
    if len(spl) > 2: return False
    for p in spl:
        if p and not p.isdigit(): return False
    return True

# ############################################################################ #

def load_xml(file=sys.stdin, limit=None):
    """
    Reads an xml into a set of springbots
    """

    try:
        doc = xml.dom.minidom.parse(file)
    except ExpatError:
        sys.stderr.write("springbot.loadXML: XML parse error\n")
        return []

    # Lista de springbots
    springbots = []

    for cnode in doc.childNodes:
        if cnode.nodeType is xml.dom.minidom.Node.ELEMENT_NODE:
            springbotsNode = cnode
            break
    else:
        sys.stderr.write("springbot.load_xml: There is no springbots element\n")
        return []

    for springbotNode in springbotsNode.childNodes:

        if str(springbotNode.nodeName) == "springbot":
            # Cria novo springbot
            newspringbot = Springbot()

            for key, value in springbotNode.attributes.items():
                newspringbot[key] = float(value) if isfloat(value) else \
                (int(value) if value.isdigit() else value)

            # Percorre estrutura do arquivo e cria nodes e springs
            for cnode in springbotNode.childNodes:
                if str(cnode.nodeName) == "node":
                    newnode = Node(pos=tuple((int(x) for x in str(cnode.attributes["pos"].value).split(","))))
                    newnode.id = int(str(cnode.attributes["id"].value).split('N')[-1])
                    newspringbot._node_count_id = max(newspringbot._node_count_id, newnode.id)
                    newspringbot.add(newnode)

                elif str(cnode.nodeName) == "spring":
                    id_a = int(str(cnode.attributes["from"].value).split('N')[-1])
                    id_b = int(str(cnode.attributes["to"].value).split('N')[-1])

                    # Procura A
                    for node in newspringbot.nodes:
                        if node.id == id_a:
                            a = node
                            break
                    else:
                        raise exceptions.IndexError("node id %d(from) not found\n" % (id_a))

                    # Procura id B
                    for node in newspringbot.nodes:
                        if node.id == id_b:
                            b = node
                            break
                    else:
                        raise exceptions.IndexError("node id %d(to) not found\n" % (id_b))


                    # Cria spring
                    offs = float(str(cnode.attributes["offset"].value)) if cnode.hasAttribute("offset") else pi
                    ampl = float(str(cnode.attributes["amplitude"].value)) if cnode.hasAttribute("amplitude") else 0.0
                    norm = float(str(cnode.attributes["normal"].value)) if cnode.hasAttribute("normal") else None
                    newspringbot.add(Spring(a, b, offset=offs, amplitude=ampl, normal=norm))

            # Adiciona novo springbot a lista
            springbots.append(newspringbot)

            # Verifica se atingiu limite
            if limit is not None and len(springbots) >= limit:
                break

    return springbots
