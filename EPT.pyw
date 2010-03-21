#!/usr/bin/env python

"""
Copyright (C) 2010 Paul K. Romano

Code to process mass output data from ERANOS and rewrite it in a
form that VISION can use.
"""

from __future__ import division
import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import eranos
import vision
import dataViewer

class EPTDialog(QDialog):

    def __init__(self, parent=None):
        """
        Create main dialog window for the ERANOS processing tool.
        """

        super(EPTDialog, self).__init__(parent)

        # Layout
        self.loadDataButton = QPushButton("Load ERANOS Data...")
        self.viewDataButton = QPushButton("View ERANOS Data")
        self.viewDataButton.setDisabled(True)
        self.writeDataButton = QPushButton("Write ERANOS Data...")
        self.writeDataButton.setDisabled(True)
        self.writeVisionButton = QPushButton("Write VISION Input...")
        self.writeVisionButton.setDisabled(True)
        layout = QVBoxLayout()
        layout.addWidget(self.loadDataButton)
        layout.addWidget(self.viewDataButton)
        layout.addWidget(self.writeDataButton)
        layout.addWidget(self.writeVisionButton)
        self.setLayout(layout)
        self.setWindowTitle("EPT")

        # Set connections
        self.connect(self.loadDataButton, SIGNAL("clicked()"), self.loadData)
        self.connect(self.viewDataButton, SIGNAL("clicked()"), self.viewData)
        self.connect(self.writeDataButton, SIGNAL("clicked()"), self.writeData)
        self.connect(self.writeVisionButton, SIGNAL("clicked()"), self.writeVision)

        # Create empty cycles list
        self.cycles = []


    def loadData(self):
        """
        Open file dialog to select ERANOS data file.
        """

        filename = str(QFileDialog.getOpenFileName(
                self, "Load ERANOS Data", "./", "ERANOS Data (*.data.*)"))
        if not filename:
            return
        self.cycles = eranos.loadData(filename, self)
        if self.cycles:
            self.viewDataButton.setEnabled(True)
            self.writeDataButton.setEnabled(True)
            self.writeVisionButton.setEnabled(True)


    def viewData(self):
        """
        Open the data viewing dialog window.
        """

        dialog = dataViewer.DataViewer(self.cycles, self)
        dialog.exec_()


    def writeData(self):
        """
        Write out all ERANOS data to a specified file.
        """
        
        filename = str(QFileDialog.getSaveFileName(
                self, "Save ERANOS output", "./", "ERANOS Data (*)"))
        eranos.writeData(filename, self.cycles)


    def writeVision(self):
        """
        Format material data into form suitable for VISION.
        """

        # Choose cycle
        choice, ok = QInputDialog.getInt(
            self, "Choose Cycle", "Choose which cycle to load from:",
            1, 1, len(self.cycles))
        if ok:
            cycle = self.cycles[choice-1]
        else:
            return

        # Choose charge time
        choice, ok = QInputDialog.getItem(
            self, "Choose Charge Time", "Choose timestep for charge material",
            [str(i) for i in cycle.times()], 0, False)
        if ok:
            t_charge = eval(str(choice))
        else:
            return

        # Choose discharge time
        choice, ok = QInputDialog.getItem(
            self, "Choose Discharge Time", "Choose timestep for charge "
            "material", [str(i) for i in cycle.times()], 0, False)
        if ok:
            t_discharge = eval(str(choice))
        else:
            return

        # Choose material from
        choice, ok = QInputDialog.getItem(
            self, "Choose Discharge Time", "Choose timestep for discharge "
            "material", cycle.materialNames(), 0, False)
        if ok:
            material = str(choice)
        else:
            return
                                        
        # Choose file and write data
        filename = str(QFileDialog.getSaveFileName(
                self, "Save VISION Input", "./", "VISION Input (*.txt)"))
        if filename:
            charge = cycle.materials[(t_charge,material)]
            discharge = cycle.materials[(t_discharge,material)]
            vision.writeInput(filename, charge, discharge)
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # app.setWindowIcon(QIcon(".svg"))
    form = EPTDialog()
    form.show()
    app.exec_()
