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

class EPTDialog(QDialog):

    def __init__(self, parent=None):
        """
        Create main dialog window for the ERANOS processing tool.
        """

        super(EPTDialog, self).__init__(parent)

        # Layout
        loadDataButton = QPushButton("Load ERANOS Data...")
        viewDataButton = QPushButton("View ERANOS Data")
        writeDataButton = QPushButton("Write ERANOS Data...")
        writeVisionButton = QPushButton("Write VISION Input...")
        layout = QVBoxLayout()
        layout.addWidget(loadDataButton)
        layout.addWidget(viewDataButton)
        layout.addWidget(writeDataButton)
        layout.addWidget(writeVisionButton)
        self.setLayout(layout)
        self.setWindowTitle("EPT")

        # Set connections
        self.connect(loadDataButton, SIGNAL("clicked()"), self.loadData)
        self.connect(writeDataButton, SIGNAL("clicked()"), self.writeData)
        self.connect(writeVisionButton, SIGNAL("clicked()"), self.writeVision)

        # Create empty cycles list
        self.cycles = []


    def loadData(self):
        """
        Open file dialog to select ERANOS data file.
        """

        filename = str(QFileDialog.getOpenFileName(
                self, "Load ERANOS Data", "./", "ERANOS Data (*.data.*)"))
        self.cycles = eranos.loadData(filename, self)


    def writeData(self):
        """
        Write out all ERANOS data to a specified file.
        """
        
        if not self.cycles:
            QMessageBox.warning(self, "No Data", "No ERANOS data has been"
                                " loaded yet!")
            return
        filename = str(QFileDialog.getSaveFileName(
                self, "Save ERANOS output", "./", "ERANOS Data (*)"))
        eranos.writeData(filename, self.cycles)


    def writeVision(self):
        """
        Format material data into form suitable for VISION.
        """

        # Check for data
        if not self.cycles:
            QMessageBox.warning(self, "No Data", "No ERANOS data has been"
                                " loaded yet!")
            return

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
