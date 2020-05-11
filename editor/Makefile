#! /bin/make

all: ui_mainwindow.py ui_aboutdialog.py resource_rc.py

ui_mainwindow.py: forms/mainwindow.ui
	pyuic5 forms/mainwindow.ui > ui_mainwindow.py

ui_aboutdialog.py: forms/aboutdialog.ui
	pyuic5 forms/aboutdialog.ui > ui_aboutdialog.py

resource_rc.py:	img/resource.qrc
	pyrcc5 img/resource.qrc > resource_rc.py

clean:
	rm -f resource_rc.py* ui_aboutdialog.py* ui_mainwindow.py*

run:
	./mainwindow.py

