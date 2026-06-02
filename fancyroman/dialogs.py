#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  1 17:08:43 2026

@author: dfadda
"""


from PyQt6.QtWidgets import (QDialog, QGroupBox, QVBoxLayout, QHBoxLayout, 
                             QCheckBox, QPushButton, QGridLayout)

class QFlagList(QDialog):
    """Dialog window to select quality flags for masking"""
    
    def __init__(self, flags, states, parent=None):
        super().__init__(parent)
        self.flags = flags
        self.states = states
        self.setupUI()
        
    def setupUI(self):
        hgroup = QGroupBox()
        hbox = QHBoxLayout()
        self.button1 = QPushButton("OK")
        self.button1.clicked.connect(self.OK)
        self.button2 = QPushButton("Cancel")
        self.button2.clicked.connect(self.Cancel)
        hbox.addWidget(self.button1) 
        hbox.addWidget(self.button2)
        hgroup.setLayout(hbox)   
        
        
        
        vgroup = QGroupBox()
        vbox = QVBoxLayout()
        self.checkbox = []
        for flag, state in zip(self.flags, self.states):
            checkbox = QCheckBox(flag)
            checkbox.setChecked(state)
            vbox.addWidget(checkbox)
            self.checkbox.append(checkbox)
        vgroup.setLayout(vbox)

        grid = QGridLayout()
        grid.addWidget(vgroup, 0, 0)
        grid.addWidget(hgroup, 1, 0)
        self.setLayout(grid)
        self.setWindowTitle('Quality Flags')

        
    def OK(self):
        self.done(1)
        
    def Cancel(self):
        self.done(0)
        
    def save(self):
        states = []
        for c in self.checkbox:
            if c.isChecked():
                states.append(True)
            else:
                states.append(False)
        return states