from PyQt4 import QtGui, QtCore
from math import pi, sin
import mainwindow, space

class Senoide(QtGui.QWidget):
	
	#
	# Construtor
	#
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self, parent)
		self.setMouseTracking(True)
		self.setAutoFillBackground(False)

	#
	# Desenha onda e marcadores musculares do
	# springbot atual
	#
	def paintEvent(self, event):
		paint = QtGui.QPainter()

		paint.begin(self)

		# Verifica tamanho
		width, height = self.size().width(), self.size().height()

		# Limpa tudo
		paint.setBrush(QtGui.QColor(0, 0, 0))
		paint.drawRect(0, 0, width, height)

		paint.setBrush(QtGui.QColor(0, 0, 10))
		paint.drawRect(width/6, 0, width*4/6, height)
		pen = QtGui.QPen()

		# Desenha linha media
		pen.setColor(QtGui.QColor(10, 10, 10))
		pen.setWidth(4)
		paint.setPen(pen)

		paint.drawLine(width/2, 0, width/2, height)

		if space.selected_springbot:
			# Desenha marcadores de springs
			pen.setColor(QtGui.QColor(50, 50, 55))
			pen.setWidth(3)
			paint.setPen(pen)
			for spring in space.selected_springbot.springs:
				paint.drawLine(0, (2*pi) + (spring.offset*height/(2*pi)), width, (2*pi) + (spring.offset*height/(2*pi)))
				paint.drawEllipse((width/2) + (spring.amplitude*(width/2)) - 4, (2*pi) + (spring.offset*height/(2*pi)) - 4, 8, 8)

			if space.selected_spring:
				pen.setColor(QtGui.QColor(100, 100, 0))	
				paint.setPen(pen)
				paint.drawLine(0, (2*pi) + (space.selected_spring.offset*height/(2*pi)), 
				width, (2*pi) + (space.selected_spring.offset*height/(2*pi)))
				paint.drawEllipse((width/2) + (space.selected_spring.amplitude*(width/2)) - 4, 
				(2*pi) + (space.selected_spring.offset*height/(2*pi)) - 4, 8, 8)

			if space.focus_spring and space.focus_spring.parent is space.selected_springbot:
				pen.setColor(QtGui.QColor(50, 100, 0))
				paint.setPen(pen)
				paint.drawLine(0, (2*pi) + (space.focus_spring.offset*height/(2*pi)), 
				width, (2*pi) + (space.focus_spring.offset*height/(2*pi)))
				paint.drawEllipse((width/2) + (space.focus_spring.amplitude*(width/2)) - 4, 
				(2*pi) + (space.focus_spring.offset*height/(2*pi)) - 4, 8, 8)


			# Desenha seno
			pen.setColor(QtGui.QColor(200, 200, 255))
			pen.setWidth(2)
			paint.setPen(pen)

			x = (width/2) + sin(space.selected_springbot['angle'])*(width/3)
			y = 0
			for i in xrange(0,height,10):
				paint.drawLine(x, y, (width/2) + (sin((i*pi*2/height)+space.selected_springbot['angle'])*(width/3)), i)
				x = (width/2) + (sin((i*pi*2/height)+space.selected_springbot['angle'])*(width/3))
				y = i

		paint.end()

	#
	# Evento do mouse: pressionamento
	#
	def mousePressEvent (self, event):

		if space.focus_spring:
			space.selected_spring = space.focus_spring

		if space.selected_spring:
			# Verifica tamanho
			width, height = self.size().width(), self.size().height()

			if event.x() < width/6.0:
				x = width/6.0
			elif event.x() > width*5.0/6.0:
				x = width*5.0/6.0
			else:
				x = float(event.x())

			space.selected_spring.offset = (float(event.y()) * (pi*2) / height)
			space.selected_spring.amplitude = (x-(width/2))/(width/2)

	#
	# Evento do mouse: movimento
	#
	def mouseMoveEvent(self, event):
		
		if space.selected_springbot:
			width, height = self.size().width(), self.size().height()

			# Percorre springs para ver se alguma entra em foco
			for spring in space.selected_springbot.springs:
				if abs((2*pi) + (spring.offset*height/(2*pi)) - event.y()) <= 6:
						space.focus_spring = spring
						break
				else:
					space.focus_spring = None

			if space.selected_spring and event.buttons() == QtCore.Qt.LeftButton:			

				if event.x() < width/6.0:
					x = width/6.0
				elif event.x() > width*5.0/6.0:
					x = width*5.0/6.0
				else:
					x = float(event.x())

				space.selected_spring.offset = (float(event.y()) * (pi*2) / height)
				space.selected_spring.amplitude = (x -(width/2))/(width/2)


