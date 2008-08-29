import sys
sys.path.append('..')

from PyQt4 import QtCore, QtGui
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

class MainWindow(QtGui.QMainWindow, Ui_MainWindow):

    #
    # Constroi janela principal do programa
    #
    def __init__(self):
        global springbot

        QtGui.QMainWindow.__init__(self)

    # Set up the user interface from Designer.
        self.setupUi(self)

        # Cria objeto about dialog
        self.aboutDialog = QtGui.QDialog()
        ui = Ui_Dialog()
        ui.setupUi(self.aboutDialog)

        # Cria timer e seta os slots
        self.timer = QtCore.QTimer(self)
        QtCore.QObject.connect(self.timer,  QtCore.SIGNAL("timeout()"), self.space.refresh)
        QtCore.QObject.connect(self.timer,  QtCore.SIGNAL("timeout()"), self.senoide, QtCore.SLOT("update()"))
        QtCore.QObject.connect(self.timer,  QtCore.SIGNAL("timeout()"), self.space, QtCore.SLOT("update()"))

        # Conecta as acoes com os metodos
        QtCore.QObject.connect(self.toggleGravityAct, QtCore.SIGNAL("toggled(bool)"), self.toggleGravity)
        QtCore.QObject.connect(self.toggleEditModeAct, QtCore.SIGNAL("toggled(bool)"), self.toggleEditMode)
        QtCore.QObject.connect(self.killSpringbotAct, QtCore.SIGNAL("triggered(bool)"), self.killSpringbot)
        QtCore.QObject.connect(self.loadSpringbotsAct, QtCore.SIGNAL("triggered(bool)"), self.loadSpringbots)
        QtCore.QObject.connect(self.saveSpringbotsAct, QtCore.SIGNAL("triggered(bool)"), self.saveSpringbots)
        QtCore.QObject.connect(self.changeNameAct, QtCore.SIGNAL("triggered(bool)"), self.changeName)
        QtCore.QObject.connect(self.mutateAct, QtCore.SIGNAL("triggered(bool)"), self.mutate)
        QtCore.QObject.connect(self.newRandomAct, QtCore.SIGNAL("triggered(bool)"), self.newRandom)
        QtCore.QObject.connect(self.showMassCenterAct, QtCore.SIGNAL("toggled(bool)"), self.showMassCenter)
        QtCore.QObject.connect(self.showNamesAct, QtCore.SIGNAL("toggled(bool)"), self.showNames)
        QtCore.QObject.connect(self.aboutAct, QtCore.SIGNAL("triggered(bool)"), self.about)

        self.timer.start(15)

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
            self.space.focus_node = self.space.selected_noe = None
            space.selected_springbot =  random.choice(springbots) if springbots else None

        else:
            QtGui.QMessageBox.warning(self, 'Kill Springbot',
"Please select a Springbots to kill.", QtGui.QMessageBox.Ok)


    #
    # Muda nome do  Springbot
    #
    def changeName(self, trigger):
        global springbots

        # Verifica se esta selecionado
        if space.selected_springbot:
            text, ok = QtGui.QInputDialog.getText(self, "Springbot name", "name", QtGui.QLineEdit.Normal, space.selected_springbot.name)
            if ok:
                space.selected_springbot.name = text
        else:
            QtGui.QMessageBox.warning(self, 'Change name',
"Please select a Springbots first.", QtGui.QMessageBox.Ok)
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
            QtGui.QMessageBox.warning(self, 'Save springbots',
"There are no Springbots to save.", QtGui.QMessageBox.Ok)

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
            QtGui.QMessageBox.warning(self, 'Mutate Springbot',
"Please select a Springbot to mutate.", QtGui.QMessageBox.Ok)

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

        show_mass_center = toggle       #

    #
    # Mostra nomes
    #
    def showNames(self, toggle):
        global show_names

        show_names = toggle
