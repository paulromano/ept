#!/usr/bin/env python

"""
Copyright (C) 2010 Paul K. Romano

Code to process mass output data from ERANOS and rewrite it in a
form that VISION can use.
"""

from __future__ import division
import sys
import platform

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import eranos
import vision
from material import Material
from isotope import Isotope

__version__ = "0.2.4"

class EPTMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(EPTMainWindow, self).__init__(parent)

        # Create tab widget and associated tabs
        self.main = QWidget()

        # Create material selector widgets/layout
        cycleLabel = QLabel("Cycle:")
        self.cycleCombo = QComboBox()
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
                "Fissile mass / total actinide mass",
                "Charlton: DOE Attrativeness (u1)",
                "Charlton: Pu Heating Rate (u2)",
                "Charlton: Weight Fraction Even Pu (u3)",
                "Charlton: Concentration (u4)",
                "Charlton: Dose Rates (u5)",
                "Bathke: Sub-national (FOM1)",
                "Bathke: Unadvanced Nation (FOM2)",
                "DPA",
                "Burnup (MWd/kg)"])
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
        self.main.setLayout(layout)
        self.setCentralWidget(self.main)
        self.setWindowTitle("ERANOS Post-Processing Tool")

        # Add menu items
        self.menubar = QMenuBar(self)
        self.menuFile = QMenu("&File",self.menubar)
        self.menuEdit = QMenu("&Edit",self.menubar)
        self.menuHelp = QMenu("&Help",self.menubar)
        self.setMenuBar(self.menubar)
        self.menubar.addActions([self.menuFile.menuAction(),
                                 self.menuEdit.menuAction(),
                                 self.menuHelp.menuAction()])
        
        self.actionLoadEranos = QAction("&Load ERANOS Data from Output...",self)
        self.actionLoadXML = QAction("Load ERANOS Data from XML...",self)
        self.actionLoadXML.setDisabled(True)
        self.actionSaveXML = QAction("Save ERANOS Data as XML...", self)
        self.actionSaveXML.setDisabled(True)
        self.actionSaveText = QAction("Save ERANOS Data as text...", self)
        self.actionSaveText.setDisabled(True)
        self.actionWriteVision = QAction("Write VISION Input...", self)
        self.actionWriteVision.setDisabled(True)
        self.actionWriteVision2 = QAction("Write VISION (U Added)...", self)
        self.actionWriteVision2.setDisabled(True)
        self.actionExit = QAction("E&xit",self)
        self.menuFile.addActions([self.actionLoadEranos, self.actionLoadXML,
                                  self.actionSaveXML, self.actionSaveText,
                                  self.actionWriteVision, self.actionWriteVision2, 
                                  self.actionExit])
        self.menuFile.insertSeparator(self.actionWriteVision)
        self.menuFile.insertSeparator(self.actionExit)
        self.actionEditCooling = QAction("&Cooling Time",self)
        self.actionEditCooling.setDisabled(True)
        self.menuEdit.addActions([self.actionEditCooling])
        self.actionAbout = QAction("&About",self)
        self.menuHelp.addActions([self.actionAbout])

        # Menu Signals
        self.connect(self.actionLoadEranos, SIGNAL("triggered()"), self.loadEranos)
        self.connect(self.actionSaveText, SIGNAL("triggered()"), self.saveText)
        self.connect(self.actionWriteVision, SIGNAL("triggered()"), self.writeVision)
        self.connect(self.actionWriteVision2, SIGNAL("triggered()"), self.writeVision2)
        self.connect(self.actionExit, SIGNAL("triggered()"), self.close)
        self.connect(self.actionEditCooling, SIGNAL("triggered()"), self.editCooling)
        self.connect(self.actionAbout, SIGNAL("triggered()"), self.about)

        # Set connections
        self.connect(self.cycleCombo, SIGNAL("activated(int)"),
                     self.cycleChanged)
        self.connect(self.propCombo, SIGNAL("activated(int)"), self.update)
        self.connect(self.timeCombo, SIGNAL("activated(int)"), self.update)
        self.connect(self.matCombo, SIGNAL("activated(int)"), self.update)

        # Perform initial loading
        self.cycles = []

    def update(self):
        """
        Populate combo boxes and list isotopes for currently selected
        material.
        """

        if not self.cycles:
            return

        # Set timestep and material comboboxes
        i = self.cycleCombo.currentIndex()
        timenode = self.timeCombo.currentIndex()
        mat = str(self.matCombo.currentText())

        # Set property value label
        material = self.cycles[i].materials[(timenode,mat)]
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

        # Proliferation resistance criteria
        if self.propCombo.currentIndex() == 12:
            pv.setText("{0:10.4e}".format(material.charlton1()))
        if self.propCombo.currentIndex() == 13:
            pv.setText("{0:10.4e}".format(material.charlton2()))
        if self.propCombo.currentIndex() == 14:
            pv.setText("{0:10.4e}".format(material.charlton3()))
        if self.propCombo.currentIndex() == 15:
            pv.setText("{0:10.4e}".format(material.charlton4()))
        if self.propCombo.currentIndex() == 16:
            pv.setText("{0:10.4e}".format(material.charlton5()))
        if self.propCombo.currentIndex() == 17:
            if material.bathke1():
                pv.setText("{0:10.4e}".format(material.bathke1(False)))
            else:
                pv.setText("")
        if self.propCombo.currentIndex() == 18:
            if material.bathke2():
                pv.setText("{0:10.4e}".format(material.bathke2(False)))
            else:
                pv.setText("")
        if self.propCombo.currentIndex() == 19:
            pv.setText("{0:10.4e}".format(material.dpavalue()))
        if self.propCombo.currentIndex() == 20:
            pv.setText("{0:10.4e}".format(material.intpower()/self.cycles[1].materials[(0,mat)].mass(Actinide = True)))
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

        if not self.cycles:
            return

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

        
    def loadEranos(self):
        """
        Open file dialog to select ERANOS data file.
        """

        filename = str(QFileDialog.getOpenFileName(
                self, "Load ERANOS Data", "./", "ERANOS Data (*.data.*)"))
        if not filename:
            return
        self.cycles = eranos.loadData(filename)
        # self.eranosOut = eranos.EranosOutput(filename, self)
        # self.eranosOut.loadData()
        self.cycleCombo.clear()
        self.cycleCombo.addItems([str(i+1) for i in range(len(self.cycles))])
        self.cycleChanged(0)
        self.actionSaveText.setEnabled(True)
        self.actionWriteVision.setEnabled(True)
        self.actionWriteVision2.setEnabled(True)
        self.actionEditCooling.setEnabled(True)

    def saveText(self):
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
            self, "Choose Discharge Time", "Choose timestep for discharge "
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

    def writeVision2(self):
        """
        Format material data into form suitable for VISION.
        """

        # Choose starting cycle
        choice, ok = QInputDialog.getInt(
            self, "Choose Cycle", "Choose starting cycle:",
            1, 1, len(self.cycles))
        if ok:
            start = choice-1
        else:
            return

        # Choose ending cycle
        choice, ok = QInputDialog.getInt(
            self, "Choose Cycle", "Choose ending cycle:",
            1, 1, len(self.cycles))
        if ok:
            end = choice-1
        else:
            return

        # Choose file and write data
        filename = str(QFileDialog.getSaveFileName(
                self, "Save VISION Input", "./", "VISION Input (*.txt)"))
        if filename:
            charge = Material()
            discharge = Material()
            time = 0
            for cycle in self.cycles[start:end]:
                time += cycle.timestep*cycle.iterations
                for iso in cycle.charge:
                    charge.addMass(str(iso), iso.mass)
                for iso in cycle.discharge:
                    discharge.addMass(str(iso), iso.mass)

            # Average over time
            for iso in charge:
                iso.mass /= time
            for iso in discharge:
                iso.mass /= time
            vision.writeInput(filename, charge, discharge)

    def editCooling(self):
        index = self.cycleCombo.currentIndex()
        time, ok = QInputDialog.getInteger(self, "Edit Cooling Time",
                                           "Enter cooling time for cycle {0}".format(index+1),
                                           self.cycles[index].cooling_time, 0)
        if ok:
            self.cycles[index].cooling_time = time
            self.cycleChanged(index)
        else:
            pass
        

    def about(self):
        QMessageBox.about(self, "About ERANOS Post-Processing Tool",
                          """<b>ERANOS Post-Processing Tool</b> v %s
                          <p>Copyright &copy; 2010 Paul K. Romano,
                          Benoit Forget.  All Rights Reserved.
                          <p>Python %s -- Qt %s -- PyQt %s on %s""" %
                          (__version__, platform.python_version(),QT_VERSION_STR,
                           PYQT_VERSION_STR, platform.system()))
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = EPTMainWindow()
    form.show()
    app.exec_()
