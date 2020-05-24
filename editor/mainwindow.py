import sys
sys.path.append('..')

from PyQt5 import QtGui, QtWidgets, QtCore
from ui_mainwindow import Ui_MainWindow
from ui_aboutdialog import Ui_Dialog

from springbots.springbot import *
from springbots.evolvespringbot import *
from springbots.gear import *
import space
import random

# seta variaveis iniciais
angle = 0.0
edit_mode = True
gravity = False

# Flags de desenho
show_mass_center = False
show_names = False

# Lista de springbots
springbots = []

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    #
    # Constroi janela principal do programa
    #
    def __init__(self):
        global springbot

        QtWidgets.QMainWindow.__init__(self)

    # Set up the user interface from Designer.
        self.setupUi(self)

        # Cria objeto about dialog
        self.aboutDialog = QtWidgets.QDialog()
        ui = Ui_Dialog()
        ui.setupUi(self.aboutDialog)

        # Cria timer e seta os slots
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.space.refresh)
        self.timer.timeout.connect(self.senoide.update)
        self.timer.timeout.connect(self.space.update)

        # Conecta as acoes com os metodos
        self.toggleGravityAct.toggled.connect(self.toggleGravity)
        self.toggleEditModeAct.toggled.connect(self.toggleEditMode)
        self.killSpringbotAct.triggered.connect(self.killSpringbot)
        self.loadSpringbotsAct.triggered.connect(self.loadSpringbots)
        self.saveSpringbotsAct.triggered.connect(self.saveSpringbots)
        self.changeNameAct.triggered.connect(self.changeName)
        self.mutateAct.triggered.connect(self.mutate)
        self.newRandomAct.triggered.connect(self.newRandom)
        self.showMassCenterAct.toggled.connect(self.showMassCenter)
        self.showNamesAct.toggled.connect(self.showNames)
        self.aboutAct.triggered.connect(self.about)
        self.crossoverAct.triggered.connect(self.crossover)

        self.timer.start(30)


    #
    # Crossover
    #
    def crossover(self, toggle):
        global springbots

        if len(springbots) < 2:
            QtWidgets.QMessageBox.warning(self, 'Crossover', 'The number of springbots in the space must be equal or greater than two')
        else:

            # Pega tamanho da tela
            width, height = self.space.size().width(), self.space.size().height()

            # Crossover all
            new = None
            for springbot in springbots:
                if new is None:
                    new = springbot
                else:
                    new = springbot.crossover(new)

            if len(new.nodes) > 0:
                # Seta cor aleatoria
                new.cor = random.choice(space.CORES)

                # Posiciona
                x1, y1, x2, y2 = new.boundingBox()
                tr_x = random.randint(int(min(x2-x1, width-(x2-x1))), int(max(x2-x1, width-(x2-x1))))
                tr_y = random.randint(int(min(y2-y1, height-(y2-y1))), int(max(y2-y1, height-(y2-y1))))

                for node in new.nodes:
                    node.pos.x += tr_x
                    node.pos.y += tr_y

                springbots.append(new)

    #
    # Muda gravidade
    #
    def toggleGravity(self, toggle):
        global gravity

        gravity = toggle

    #
    # Muda modo edicao
    #
    def toggleEditMode(self, toggle):
        global edit_mode

        edit_mode = toggle

    #
    # Mata criatura
    #
    def killSpringbot(self, trigger):
        global springbots, edit_mode

        # Apaga springbot
        if space.selected_springbot:
            springbots.remove(space.selected_springbot)

            space.focus_spring = space.selected_spring = None
            self.space.focus_node = self.space.selected_node = None
            space.selected_springbot =  random.choice(springbots) if springbots else None

        else:
            QtWidgets.QMessageBox.warning(self, 'Kill Springbot',
                                      "Please select a Springbots to kill.", QtWidgets.QMessageBox.Ok)


    #
    # Muda nome do  Springbot
    #
    def changeName(self, trigger):
        global springbots

        # Verifica se esta selecionado
        if space.selected_springbot:
            text, ok = QtGui.QInputDialog.getText(self, "Springbot name", "name",
                                                  QtGui.QLineEdit.Normal, space.selected_springbot['name'])
            if ok:
                space.selected_springbot.name = text
        else:
            QtWidgets.QMessageBox.warning(self, 'Change name',
                                      "Please select a Springbots first.", QtWidgets.QMessageBox.Ok)
    #
    # Carrega Springbots
    #
    def loadSpringbots(self, trigger):
        global springbots

        filename =  QtGui.QFileDialog.getOpenFileName(self, "Open springbot descriptor",
            '.', "XML Files (*.xml)")

        if filename:
            newspringbots = [EvolveSpringbot(s) for s in load_xml(str(filename), limit=1)]

            # Pega tamanho da tela
            width, height = self.space.size().width(), self.space.size().height()

            for springbot in newspringbots:
                # Seta cor aleatoria
                springbot.cor = random.choice(space.CORES)

                # Posiciona
                x1, y1, x2, y2 = springbot.boundingBox()
                tr_x = random.randint(int(min(x2-x1, width-(x2-x1))), int(max(x2-x1, width-(x2-x1))))
                tr_y = random.randint(int(min(y2-y1, height-(y2-y1))), int(max(y2-y1, height-(y2-y1))))

                for node in springbot.nodes:
                    node.pos.x += tr_x
                    node.pos.y += tr_y

            # Adiciona a lista de springbots
            springbots += newspringbots
            if not space.selected_springbot and springbots:
                space.selected_springbot = random.choice(springbots)

    #
    # Salva Springbots
    #
    def saveSpringbots(self, trigger):
        global springbots

        if len(springbots) > 0:
            filename =  QtGui.QFileDialog.getSaveFileName(self, "Save springbot descriptor",
                    '.', "XML Files (*.xml)", "*.xml")
            if filename:
                store_xml(springbots, filename)
        else:
            QtWidgets.QMessageBox.warning(self, 'Save springbots',
                                      "There are no Springbots to save.", QtWidgets.QMessageBox.Ok)

    #
    # Add New Random
    #
    def newRandom(self, trigger):
        global springbots

        # Pega tamanho da tela
        width, height = self.space.size().width(), self.space.size().height()

        springbot = random_springbot()

        # Seta cor aleatoria
        springbot.cor = random.choice(space.CORES)

        # Posiciona
        x1, y1, x2, y2 = springbot.boundingBox()
        tr_x = random.randint(int(min(x2-x1, width-(x2-x1))), int(max(x2-x1, width-(x2-x1))))
        tr_y = random.randint(int(min(y2-y1, height-(y2-y1))), int(max(y2-y1, height-(y2-y1))))

        for node in springbot.nodes:
            node.pos.x += tr_x
            node.pos.y += tr_y

        springbots.append(springbot)

    #
    # Mutate
    #
    def mutate(self, trigger):
        if space.selected_springbot:
            space.selected_springbot.mutate()

        else:
            QtWidgets.QMessageBox.warning(self, 'Mutate Springbot',
                                      "Please select a Springbot to mutate.", QtWidgets.QMessageBox.Ok)

    #
    # About
    #
    def about(self, trigger):
        self.aboutDialog.show()

    #
    # Mostra centro de massa
    #
    def showMassCenter(self, toggle):
        global show_mass_center

        show_mass_center = toggle

    #
    # Mostra nomes
    #
    def showNames(self, toggle):
        global show_names

        show_names = toggle
