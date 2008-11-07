import sys
sys.path.append('..')

from PyQt4 import QtGui, QtCore
from springbots.evolvespringbot import *
from springbots import gear
from springbots.springbot import Springbot
import mainwindow
import math, random
from springbots.latimname import latimname

selected_spring = None
focus_spring = None
selected_springbot = None

CORES = [
(255,0,0),
(0,255,0),
(0,0,255),
(50,255,255),
(255,0,255),
(40,200,255),
(255,255,200),
(255,100,50),
(50,255,100),
(100,50,255),
(255,40,120),
(40,255,120),
(120,50,255),
]

def dist(a, b):
    return math.sqrt((a[0]-b[0])**2+(a[1]-b[1])**2)

class Space(QtGui.QWidget):

    #
    # Inicializa widget
    #
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setMouseTracking(True)
        self.setAutoFillBackground(False)

        # estado do mouse
        self.creating = False

        # Existe algum objeto selecionado
        self.selected_node = None
        self.focus_node = None

        # ultima posicao do mouse
        self.mouse_pos = (0,0)

        # variaveis do mundo
        self.atr_normal = 0.7
        self.atr_surface = 0.6
        self.min_vel = 0.99

        # Ticks de simulacao
#               self.ticks = 0


    #
    # Desenha criatura e efeitos de edicao
    #
    def paintEvent(self, event):
        global selected_spring, focus_spring, selected_springbot

        global NODE_RADIUS

        paint = QtGui.QPainter()
        pen = QtGui.QPen()

        paint.begin(self)
#               paint.setRenderHint(QtGui.QPainter.Antialiasing, True)

        # Verifica tamanho
        width, height = self.size().width(), self.size().height()

        # Limpa tudo
        if mainwindow.edit_mode:
            paint.setBrush(QtGui.QColor(25, 25, 25))
        else:
            paint.setBrush(QtGui.QColor(0, 0, 0))
        paint.drawRect(0, 0, width, height)

        # desenha selecao em torno de selected springbot e centro de massa
        if selected_springbot:

            # Pega bounding box
            x1, y1, x2, y2 = selected_springbot.boundingBox()

            pen.setColor(QtGui.QColor(40, 40, 40))
            paint.setPen(pen)
            paint.drawRoundRect(x1, y1, x2-x1, y2-y1)

            # Se esta habilitado centro de massa
            if mainwindow.show_mass_center:
                cx, cy = selected_springbot.massCenter()
                pen.setColor(QtGui.QColor(*selected_springbot.cor))
                paint.setPen(pen)
                paint.drawLine(cx-gear.RADIUS, cy-gear.RADIUS, cx+gear.RADIUS, cy+gear.RADIUS)
                paint.drawLine(cx-gear.RADIUS, cy+gear.RADIUS, cx+gear.RADIUS, cy-gear.RADIUS)

            # Se esta habilitado mostrar nomes
            if mainwindow.show_names:
                pen.setColor(QtGui.QColor(*selected_springbot.cor))
                paint.setPen(pen)
                paint.drawText(x1-(100), y1-22, (x2-x1)+200, 22, QtCore.Qt.AlignHCenter, selected_springbot['name'])

        # Desenha ticks de simulacao
#               pen.setColor(QtGui.QColor(255,255,255))
#               paint.setPen(pen)
#               paint.drawText(1, 40, str(self.ticks))

        # Desenha objetos do springbot
        for springbot in mainwindow.springbots:

            # Desenha todos springs
            for spring in springbot.springs:
                if spring is selected_spring:
                    pen.setWidth(3)
                    pen.setColor(QtGui.QColor(255, 255, 0))
                elif spring is focus_spring:
                    pen.setWidth(3)
                    pen.setColor(QtGui.QColor(100, 255, 0))
                else:
                    pen.setWidth(2)

                    length = (spring.a.pos - spring.b.pos).length()
                    fator = (length - spring.normal)/(length or 1)

                    if fator <= 0:
                        color = (255, 255-min(-fator * 255, 255), 255-min(-fator * 255, 255))
                    elif fator > 0:
                        color = (255-min(fator * 255, 255), 255, 255-min(fator * 255, 255))

                    pen.setColor(QtGui.QColor(*color))

                paint.setPen(pen)
                paint.drawLine(spring.a.pos.x, spring.a.pos.y, spring.b.pos.x, spring.b.pos.y)

                # Mostra empuxo de fluido
#                               vnormal = (spring.a.pos - spring.b.pos).perpendicular()
#                               vnodes = spring.a.vel + spring.b.vel
#                               vproj = -vnodes.projection(vnormal)
#                               aacc += vproj * viscosidade
#                               bacc += vproj * viscosidade
#                               pen.setColor(QtGui.QColor(100, 255, 255))
#                               paint.setPen(pen)
#                               paint.drawLine((spring.a.pos.x+spring.b.pos.x)/2, (spring.a.pos.y+spring.b.pos.y)/2,
#                               (spring.a.pos.x+spring.b.pos.x)/2 + (vproj.x*10), (spring.a.pos.y+spring.b.pos.y)/2 + (vproj.y*10))

            # desenha todos os nodes
            pen.setWidth(2)
            for node in springbot.nodes:
                if node is self.selected_node:
                    pen.setColor(QtGui.QColor(255, 255, 0))
                elif node is self.focus_node:
                    pen.setColor(QtGui.QColor(100, 255, 0))
                else:
                    pen.setColor(QtGui.QColor(*springbot.cor))
                paint.setPen(pen)
                paint.drawEllipse(node.pos.x-gear.RADIUS, node.pos.y-gear.RADIUS, 2*gear.RADIUS, 2*gear.RADIUS)

#                               pen.setColor(QtGui.QColor(255, 255, 100))
#                               paint.setPen(pen)
#                               paint.drawLine(node.pos.x, node.pos.y, node.pos.x+(node.vel.x*10), node.pos.y+(node.vel.y*10))


        # desenha, criando node
        if self.creating and mainwindow.edit_mode:
            if not self.focus_node or (self.focus_node.parent is not self.selected_node.parent):
                pen.setColor(QtGui.QColor(0, 255, 255))
                paint.drawEllipse(self.mouse_pos[0]-gear.RADIUS, self.mouse_pos[1]-gear.RADIUS,
                        2*gear.RADIUS, 2*gear.RADIUS)

            pen.setWidth(3)
            paint.setPen(pen)
            paint.drawLine(self.selected_node.pos.x, self.selected_node.pos.y, self.mouse_pos[0], self.mouse_pos[1])

        paint.end()

    #
    # Evento do mouse: pressionamento
    #
    def mousePressEvent (self, event):
        global selected_spring, focus_spring, selected_springbot
        global CORES

        # A principio libera qualquer spring e springbot
        selected_spring = None

        # verifica se selecionou algum node ou spring
        if self.focus_node:
            if mainwindow.edit_mode and event.button() == QtCore.Qt.MidButton:
                self.focus_node.parent.remove(self.focus_node)
                # Deleta todos nodes nao conectados
                for node in self.focus_node.parent.unconnected():
                    self.focus_node.parent.remove(node)

                # Verifica se matou springbot
                if len(self.focus_node.parent.nodes) == 0:
                    mainwindow.springbots.remove(self.focus_node.parent)
                    if self.focus_node.parent is selected_springbot:
                        selected_springbot = random.choice(mainwindow.springbots) if mainwindow.springbots else None
                self.focus_node = None

            else:
                self.selected_node = self.focus_node
                selected_springbot = self.focus_node.parent
        elif focus_spring:
            if mainwindow.edit_mode and event.button() == QtCore.Qt.MidButton:
                focus_spring.parent.remove(focus_spring)
                # Deleta todos nodes nao conectados
                for node in focus_spring.parent.unconnected():
                    focus_spring.parent.remove(node)
                focus_spring = None
            else:
                selected_spring = focus_spring
                selected_springbot = focus_spring.parent
        elif mainwindow.edit_mode and event.button() == QtCore.Qt.RightButton:
            # cria nodo(novo springbot)
            newspringbot = EvolveSpringbot(name = latimname(5))
            newspringbot.cor = random.choice(CORES)
            self.selected_node = self.focus_node = Node(pos=(event.x(), event.y()))
            newspringbot.add(self.focus_node)
            mainwindow.springbots.append(newspringbot)
            selected_springbot = newspringbot

        self.creating = (self.selected_node and event.button() == QtCore.Qt.RightButton)

        self.mouse_pos = (event.x(), event.y())

    #
    # Evento do mouse: liberacao
    #
    def mouseReleaseEvent(self, event):
        # verifica se completou a ligacao de spring com algum node
        if self.selected_node and event.button() == QtCore.Qt.RightButton and mainwindow.edit_mode:
            if self.focus_node is None or (self.selected_node.parent is not self.focus_node.parent):
                # cria node e spring
                self.focus_node = Node(pos=(event.x(), event.y()))
                self.selected_node.parent.add(self.focus_node)
                self.selected_node.parent.add(Spring(self.selected_node, self.focus_node, offset=random.random()*math.pi*2))
            elif self.focus_node is not self.selected_node:
                # cria somente spring
                self.selected_node.parent.add(Spring(self.selected_node, self.focus_node, offset=random.random()*math.pi*2))

        # desceleciona tudo
        self.creating = False
        self.selected_node = None
        self.mouse_pos = (event.x(), event.y())


    #
    # Evento do mouse: movimento
    #
    def mouseMoveEvent(self, event):
        global focus_spring

        self.focus_node = None
        focus_spring = None

        # Verifica se algum node entra em foco
        for springbot in mainwindow.springbots:
            for node in springbot.nodes:
                if dist((float(event.x()), float(event.y())), node.pos) <= gear.RADIUS:
                    self.focus_node = node
                    break
            else:
                # Verifica se alguma spring entra em foco
                for spring in springbot.springs:
                    if dist((float(event.x()), float(event.y())), spring.a.pos) + \
                       dist((float(event.x()), float(event.y())), spring.b.pos) <= \
                       dist(spring.a.pos, spring.b.pos) + 1:
                        focus_spring = spring
                        break

            if self.focus_node or focus_spring:
                break

        # se ha alguem selecionado, move
        if self.selected_node and event.buttons() == QtCore.Qt.LeftButton:
            self.selected_node.pos.x = event.x()
            self.selected_node.pos.y = event.y()

        self.mouse_pos = (event.x(), event.y())

    #
    # Atualiza criaturas
    #
    def refresh(self):

#               self.ticks += 1

        # para node selecionado
        if self.selected_node and not mainwindow.edit_mode:
            self.selected_node.vel *= 0
            self.selected_node.pos.x = self.mouse_pos[0]
            self.selected_node.pos.y = self.mouse_pos[1]

        # Verifica tamanho
        width, height = self.size().width(), self.size().height()

        if mainwindow.edit_mode:
            for springbot in mainwindow.springbots:
                springbot.refresh(0.5, (0,0), 0.5, moving=False)
        else:
            for springbot in mainwindow.springbots:
                if not mainwindow.gravity:
                    springbot.refresh(grav=gear.GRAVITY)
                else:
                    springbot.refresh(grav=(0,0), visc=gear.VISCOSITY)

        # Colide springbots
        for springbot in mainwindow.springbots:

            # trata colisao com parede
            springbot.colideWall(limit=0, side=gear.UP)
            springbot.colideWall(limit=0, side=gear.LEFT)
            springbot.colideWall(limit=width, side=gear.RIGHT)
            springbot.colideWall(limit=height, side=gear.DOWN)

            # trata colisao com outros springbots
            for otherspringbot in mainwindow.springbots:
                if springbot is not otherspringbot:
                    springbot.colide(otherspringbot)
