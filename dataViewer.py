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

        # Create material selector widgets/layout
        cycleLabel = QLabel("Cycle:")
        self.cycleCombo = QComboBox()
        self.cycleCombo.addItems([str(i+1) for i in range(len(cycles))])
        timeLabel = QLabel("Timestep:")
        self.timeCombo = QComboBox()
        matLabel = QLabel("Material:")
        self.matCombo = QComboBox()
        topLayout = QGridLayout()
        topLayout.addWidget(cycleLabel,0,0)
        topLayout.addWidget(self.cycleCombo,1,0)
        topLayout.addWidget(timeLabel,0,1)
        topLayout.addWidget(self.timeCombo,1,1)
        topLayout.addWidget(matLabel,0,2)
        topLayout.addWidget(self.matCombo,1,2)

        # Create property selector widgets/layout
        propLabel = QLabel("Property:")
        self.propCombo = QComboBox()
        self.propCombo.addItems([
                "Mass (kg)",
                "Volume (cm3)",
                "Heat rate (W/kg)",
                "Heat rate, MA only (W/kg)",
                "Photon heat rate (W/kg)",
                "Photon heat rate, MA only (W/kg)",
                "Neutron rate (N/s/kg)",
                "Neutron rate, MA only (N/s/kg)",
                "External dose rate (Sv/hr/kg at 1 m)",
                "External dose rate, MA only (Sv/hr/kg at 1 m)",
                "Critical mass (kg)",
                "Fissile mass / total actinide mass"])
        valueLabel = QLabel("Value:")
        self.propValue = QLabel()
        propLayout = QGridLayout()
        propLayout.addWidget(propLabel,0,0)
        propLayout.addWidget(self.propCombo,0,1)
        propLayout.addWidget(valueLabel,1,0)
        propLayout.addWidget(self.propValue,1,1)

        # Create material data tree
        self.dataTree = QTreeWidget()
        self.dataTree.setColumnCount(2)
        self.dataTree.setHeaderLabels(["Isotope", "Mass (kg)"])
        self.dataTree.setSelectionMode(QAbstractItemView.ContiguousSelection)

        # Setup Layout
        line = QFrame(self)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout = QVBoxLayout()
        layout.addLayout(topLayout)
        layout.addWidget(line)
        layout.addLayout(propLayout)
        layout.addWidget(self.dataTree)
        self.setLayout(layout)
        self.setWindowTitle("View ERANOS Data")

        # Set connections
        self.connect(self.cycleCombo, SIGNAL("activated(int)"),
                     self.cycleChanged)
        self.connect(self.propCombo, SIGNAL("activated(int)"), self.update)
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

        # Set property value label
        material = self.cycles[i].materials[(timestep,material)]
        pv = self.propValue
        if self.propCombo.currentIndex() == 0:
            pv.setText("{0:10.4e}".format(material.mass()))
        if self.propCombo.currentIndex() == 1:
            pv.setText("{0:10.4e}".format(material.volume))
        if self.propCombo.currentIndex() == 2:
            pv.setText("{0:10.4e}".format(
                    material.heat() / material.mass() ))
        if self.propCombo.currentIndex() == 3:
            pv.setText("{0:10.4e}".format(
                    material.heat(True) / material.mass() ))
        if self.propCombo.currentIndex() == 4:
            pv.setText("{0:10.4e}".format(
                    material.gammaHeat() / material.mass() ))
        if self.propCombo.currentIndex() == 5:
            pv.setText("{0:10.4e}".format(
                    material.gammaHeat(True) / material.mass() ))
        if self.propCombo.currentIndex() == 6:
            pv.setText("{0:10.4e}".format(
                    material.neutronProduction() / material.mass() ))
        if self.propCombo.currentIndex() == 7:
            pv.setText("{0:10.4e}".format(
                    material.neutronProduction(True) / material.mass() ))
        if self.propCombo.currentIndex() == 8:
            pv.setText("{0:10.4e}".format(
                    material.externalDose() / material.mass() ))
        if self.propCombo.currentIndex() == 9:
            pv.setText("{0:10.4e}".format(
                    material.externalDose(True) / material.mass() ))
        if self.propCombo.currentIndex() == 10:
            if material.criticalMass():
                pv.setText("{0:10.4e}".format(material.criticalMass()))
            else:
                pv.setText("")
        if self.propCombo.currentIndex() == 11:
            pv.setText("{0:10.4e}".format(
                    material.mass(Fissile = True) / 
                    material.mass(Actinide = True)))
 
        # Populate material tree
        self.dataTree.clear()
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
