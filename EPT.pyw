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

        # Create empty materials dictionary
        self.materials = None


    def loadData(self):
        """
        Open file dialog to select ERANOS data file.
        """

        filename = str(QFileDialog.getOpenFileName(
                self, "Load ERANOS Data", "./", "ERANOS Data (*.data.*)"))
        self.materials = eranos.loadData(filename, self)


    def writeData(self):
        """
        Write out all ERANOS data to a specified file.
        """
        
        if not self.materials:
            QMessageBox.warning(self, "No Data", "No ERANOS data has been"
                                " loaded yet!")
            return
        filename = str(QFileDialog.getSaveFileName(
                self, "Save VISION Input", "./", "VISION Input (*.txt)"))
        eranos.writeData(filename, self.materials)


    def writeVision(self):
        """
        Format material data into form suitable for VISION.
        """

        if not self.materials:
            QMessageBox.warning(self, "No Data", "No ERANOS data has been"
                                " loaded yet!")
            return
        filename = str(QFileDialog.getSaveFileName(
                self, "Save VISION Input", "./", "VISION Input (*.txt)"))
        charge = self.materials[(1,0,"FUEL1")]
        discharge = self.materials[(1,1030,"FUEL1")]

        vision.writeInput(filename, charge, discharge)
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # app.setWindowIcon(QIcon(".svg"))
    form = EPTDialog()
    form.show()
    app.exec_()
