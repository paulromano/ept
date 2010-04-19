#!/usr/bin/env python

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import eranos
import vision

class DataViewer(QDialog):
    """
    Class definition for dialog window that displays ERANOS data
    previously loaded.
    """

    def __init__(self, cycles, parent=None):
        """
        Create dialog window for viewing loaded materials.
        """

        super(DataViewer, self).__init__(parent)
        self.cycles = cycles

        # Create widgets
        cycleLabel = QLabel("Cycle:")
        self.cycleCombo = QComboBox()
        self.cycleCombo.addItems([str(i+1) for i in range(len(cycles))])
        timeLabel = QLabel("Timestep:")
        self.timeCombo = QComboBox()
        matLabel = QLabel("Material:")
        self.matCombo = QComboBox()
        volLabel = QLabel("Volume:")
        self.volume = QLabel()
        heatLabel = QLabel("Heat Rate (W/kg):")
        self.heatRate = QLabel()
        self.dataTree = QTreeWidget()
        self.dataTree.setColumnCount(2)
        self.dataTree.setHeaderLabels(["Isotope", "Mass (kg)"])
        self.dataTree.setSelectionMode(QAbstractItemView.ContiguousSelection)

        # Set Layout
        layout = QGridLayout()
        layout.addWidget(cycleLabel,0,0)
        layout.addWidget(self.cycleCombo,0,1)
        layout.addWidget(timeLabel,1,0)
        layout.addWidget(self.timeCombo,1,1)
        layout.addWidget(matLabel,2,0)
        layout.addWidget(self.matCombo,2,1)
        layout.addWidget(volLabel,3,0)
        layout.addWidget(self.volume,3,1)
        layout.addWidget(heatLabel,4,0)
        layout.addWidget(self.heatRate,4,1)
        layout.addWidget(self.dataTree,5,0,1,2)
        self.setLayout(layout)
        self.setWindowTitle("View ERANOS Data")

        # Set connections
        self.connect(self.cycleCombo, SIGNAL("activated(int)"),
                     self.cycleChanged)
        self.connect(self.timeCombo, SIGNAL("activated(int)"), self.update)
        self.connect(self.matCombo, SIGNAL("activated(int)"), self.update)

        self.cycleChanged(0)

    def update(self):
        """
        Populate combo boxes and list isotopes for currently selected
        material.
        """

        # Set timestep and material comboboxes
        i = self.cycleCombo.currentIndex()
        timestep = eval(str(self.timeCombo.currentText()))
        material = str(self.matCombo.currentText())

        # Populate material tree
        self.dataTree.clear()
        material = self.cycles[i].materials[(timestep,material)]
        self.volume.setText("{0:10.4e}".format(material.volume))
        self.heatRate.setText("{0:10.4e}".format(material.heatingRate()))
        isotopes = material.isotopes.keys()
        isotopes.sort()
        for name in isotopes:
            item = QTreeWidgetItem(
                self.dataTree, [name, str(material.isotopes[name].mass)])

    def cycleChanged(self, index):
        """
        Populate timestep and material comboboxes.
        """

        # Create list of timesteps and materials
        cycle = self.cycles[index]
        timesteps = [str(i) for i in cycle.times()]
        materials = cycle.materialNames()

        # Add items to comboboxes
        self.timeCombo.clear()
        self.timeCombo.addItems(timesteps)
        self.matCombo.clear()
        self.matCombo.addItems(materials)

        # Refresh data
        self.update()
        
    def keyReleaseEvent(self, event):
        """
        Overload the key release event to enable copying multiple items.
        """

        if event.matches(QKeySequence.Copy):
            text = QString()
            for item in self.dataTree.selectedItems():
                text.append(item.text(0))
                text.append("\t")
                text.append(item.text(1))
                text.append("\n")
            QApplication.clipboard().setText(text)
        else:
            QDialog.keyReleaseEvent(self, event)
