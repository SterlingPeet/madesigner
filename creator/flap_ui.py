#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Flap

author: Curtis L. Olson
website: madesigner.flightgear.org
started: November 2013
"""

import sys
from PyQt4 import QtGui, QtCore
#import xml.etree.ElementTree as ET
import lxml.etree as ET
from combobox_nowheel import QComboBoxNoWheel


class FlapUI():
    def __init__(self):
        self.valid = True
        self.container = self.make_page()
        self.xml = None
        self.clean = True

    def onChange(self):
        self.clean = False

    def isClean(self):
        return self.clean

    def setClean(self):
        self.clean = True

    def rebuild_stations(self, stations):
        station_list = str(stations).split()
        start_text = self.edit_start.currentText()
        end_text = self.edit_end.currentText()
        self.edit_start.clear()
        self.edit_start.addItem("Start: Inner")
        self.edit_end.clear()
        self.edit_end.addItem("End: Outer")
        for index,station in enumerate(station_list):
            text = "Start: " + str(station)
            self.edit_start.addItem(text)
            text = "End: " + str(station)
            self.edit_end.addItem(text)
        index = self.edit_start.findText(start_text)
        if index != None:
            self.edit_start.setCurrentIndex(index)
        index = self.edit_end.findText(end_text)
        if index != None:
            self.edit_end.setCurrentIndex(index)

    def delete_self(self):
        #print "delete self!"
        self.container.deleteLater()
        self.clean = False
        self.valid = False

    def make_page(self):
        page = QtGui.QFrame()
        layout = QtGui.QVBoxLayout()
        page.setLayout( layout )

        line1 = QtGui.QFrame()
        layout1 = QtGui.QHBoxLayout()
        line1.setLayout( layout1 )
        layout.addWidget( line1 )

        line2 = QtGui.QFrame()
        layout2 = QtGui.QHBoxLayout()
        line2.setLayout( layout2 )
        layout.addWidget( line2 )

        line3 = QtGui.QFrame()
        layout3 = QtGui.QHBoxLayout()
        line3.setLayout( layout3 )
        layout.addWidget( line3 )

        self.edit_start = QComboBoxNoWheel()
        self.edit_start.addItem("-")
        self.edit_start.addItem("1")
        self.edit_start.addItem("2")
        self.edit_start.addItem("3")
        self.edit_start.currentIndexChanged.connect(self.onChange)
        layout1.addWidget(self.edit_start)

        self.edit_end = QComboBoxNoWheel()
        self.edit_end.addItem("-")
        self.edit_end.addItem("1")
        self.edit_end.addItem("2")
        self.edit_end.addItem("3")
        self.edit_end.currentIndexChanged.connect(self.onChange)
        layout1.addWidget(self.edit_end)

        delete = QtGui.QPushButton('Delete')
        delete.clicked.connect(self.delete_self)
        layout1.addWidget(delete)
  
        layout1.addStretch(1)

        layout2.addWidget( QtGui.QLabel("<b>Pos:</b> ") )

        self.edit_posref = QComboBoxNoWheel()
        self.edit_posref.addItem("Chord %")
        self.edit_posref.addItem("Rel Front")
        self.edit_posref.addItem("Rel Rear")
        self.edit_posref.addItem("Abs Pos")
        self.edit_posref.currentIndexChanged.connect(self.onChange)
        layout2.addWidget(self.edit_posref)

        self.edit_pos = QtGui.QLineEdit()
        self.edit_pos.setFixedWidth(50)
        self.edit_pos.textChanged.connect(self.onChange)
        layout2.addWidget( self.edit_pos )

        layout2.addWidget( QtGui.QLabel("<b>At Station:</b> ") )
        self.edit_atstation = QtGui.QLineEdit()
        self.edit_atstation.setFixedWidth(50)
        self.edit_atstation.textChanged.connect(self.onChange)
        layout2.addWidget( self.edit_atstation )

        layout2.addWidget( QtGui.QLabel("<b>Slope:</b> ") )
        self.edit_slope = QtGui.QLineEdit()
        self.edit_slope.setFixedWidth(50)
        self.edit_slope.textChanged.connect(self.onChange)
        layout2.addWidget( self.edit_slope )

        layout2.addStretch(1)

        layout3.addWidget( QtGui.QLabel("<b>Edge Stringer W x H:</b> ") )

        self.edit_width = QtGui.QLineEdit()
        self.edit_width.setFixedWidth(50)
        self.edit_width.textChanged.connect(self.onChange)
        layout3.addWidget( self.edit_width )

        self.edit_height = QtGui.QLineEdit()
        self.edit_height.setFixedWidth(50)
        self.edit_height.textChanged.connect(self.onChange)
        layout3.addWidget( self.edit_height )

        layout3.addWidget( QtGui.QLabel("<b>Hinge Cutout Angle:</b> ") )

        self.edit_angle = QtGui.QLineEdit()
        self.edit_angle.setFixedWidth(50)
        self.edit_angle.textChanged.connect(self.onChange)
        layout3.addWidget( self.edit_angle )

        layout3.addStretch(1)

        return page

    def get_widget(self):
        return self.container

    def get_value(self, node):
        e = self.xml.find(node)
        if e != None and e.text != None:
            return e.text
        else:
            return ""

    def parse_xml(self, node):
        self.xml = node
        self.edit_width.setText(self.get_value('width'))
        self.edit_height.setText(self.get_value('height'))
        index = self.edit_posref.findText(self.get_value('position-ref'))
        if index == None:
            index = 1
        self.edit_posref.setCurrentIndex(index)
        self.edit_pos.setText(self.get_value('position'))
        self.edit_atstation.setText(self.get_value('at-station'))
        self.edit_slope.setText(self.get_value('slope'))
        self.edit_angle.setText(self.get_value('angle'))
        index = self.edit_start.findText(self.get_value('start-station'))
        if index != None:
            self.edit_start.setCurrentIndex(index)
        index = self.edit_end.findText(self.get_value('end-station'))
        if index != None:
            self.edit_end.setCurrentIndex(index)
        self.clean = True

    def update_node(self, node, value):
        e = self.xml.find(node)
        if e == None:
            e = ET.SubElement(self.xml, node)
        e.text = str(value)
        
    def gen_xml(self, node):
        self.xml = node
        self.update_node('width', self.edit_width.text())
        self.update_node('height', self.edit_height.text())
        self.update_node('position-ref', self.edit_posref.currentText())
        self.update_node('position', self.edit_pos.text())
        self.update_node('at-station', self.edit_atstation.text())
        self.update_node('slope', self.edit_slope.text())
        self.update_node('angle', self.edit_angle.text())
        self.update_node('start-station', self.edit_start.currentText())
        self.update_node('end-station', self.edit_end.currentText())
