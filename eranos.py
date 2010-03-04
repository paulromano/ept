#!/usr/bin/env python

"""
Copyright (C) 2010 Paul K. Romano

Code to process mass output data from ERANOS and rewrite it in a
form that VISION can use.
"""

from __future__ import division, print_function
import re
import csv

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from isotope import Isotope
from material import Material
from fileIO import fileReSeek

def loadData(filename, parent=None):
    """
    Loads material data from an ERANOS output file.

    Returns a dictionary of the form:
        {(cycle,time,mat): <Material instance>, ... }
    """

    # Open file
    eranosFile = open(filename, "r")

    # Find the names of all the fuel regions
    fuelNames = []
    m = fileReSeek(eranosFile, "^->LISTE_MILIEUX.*")
    fuelNames += re.findall("'(FUEL\d+)'", m.group())
    while True:
        line = eranosFile.readline().strip()
        fuelNames += re.findall("'(FUEL\d+)'", line)
        if line[-1] == ";": break

    # Determine cooling period
    m = fileReSeek(eranosFile, "^->COOLING\s+(\d+).*")
    if m:
        cooling = True
        cooling_time = eval(m.groups()[0])

    # Determine number of cycles
    n_cycles = 0
    while True:
        m = fileReSeek(eranosFile, ".*->CYCLE\s+(\d+).*")
        if not m: break
        n = int(m.groups()[0])
        if n > n_cycles:
            n_cycles = n
    eranosFile.seek(0)

    # Create progress bar
    progress = QProgressDialog("Loading ERANOS Data...",
                               "Cancel", 0, n_cycles, parent)
    progress.setWindowModality(Qt.WindowModal)
    progress.setMinimumDuration(0)
    progress.setValue(0)

    allMaterials = {}
    for cycle in range(1, n_cycles + 1):
        # Find beginning of cycle
        m = fileReSeek(eranosFile, "\s*'MASS BALANCE OF CYCLE (\d+)'\s*")

        # Find TIME block and set time
        m = fileReSeek(eranosFile, "\s*->TIME\s+(\d+)\s*")
        if not m: break
        time = eval(m.groups()[0])
        while True:
            QCoreApplication.processEvents()
            if (progress.wasCanceled()):
                return None

            # Loop over fuel names
            for i in fuelNames:
                m = fileReSeek(eranosFile,"\s+MATERIAL\s(FUEL\d+)\s+")
                mat = m.groups()[0]
                # print("Cycle {0} Time {1} {2}".format(cycle, time, mat))
                for n in range(6): eranosFile.readline()
                # Read in material data
                fuel = readMaterial(eranosFile)
                allMaterials[(cycle,time,mat)] = fuel
                # for iso in fuel.isotopes.values():
                #     print("{0:7} {1:12.6e} kg".format(str(iso) + ":", iso.mass))
                # print("")
            
            # If no more time blocks, read cooling 
            for n in range(9): eranosFile.readline()
            words = eranosFile.readline().split()
            if words[0] == "->TIME":
                time = eval(words[1])
            elif cooling:
                time += cooling_time
                for i in fuelNames:
                    m = fileReSeek(eranosFile,"\s+MATERIAL\s(FUEL\d+)\s+")
                    if not m: break
                    mat = m.groups()[0]
                    for n in range(6): eranosFile.readline()
                    # Read in material data
                    fuel = readMaterial(eranosFile)
                    allMaterials[(cycle,time,mat)] = fuel
                break
            else:
                break
        progress.setValue(cycle)
    eranosFile.close()
    return allMaterials
           
                
def readMaterial(fh):
    """
    Read in material data on fh starting from first line (usually Na23)
    of data and return it in a Material instance.
    """

    newMaterial = Material()
    while True:
        words = fh.readline().split()
        if len(words) == 1: break
        name = words[1]
        original_mass = eval(words[3])
        if name[0:3] == "sfp":
            name = name[3:].upper()
            if name == "AM242":
                name = "AM242M"
            sfpReader = csv.reader(open("sfp.csv"))
            sfpReader.next()
            for nrow, row in enumerate(sfpReader):
                cells = [cell for cell in row]
                if nrow == 0:
                    # Determine which column to use
                    column = [i.upper() for i in cells].index(name)
                    continue
                if nrow > 0:
                    name = cells[0]
                    fraction = eval(cells[column])
                    mass = original_mass*fraction
                # Check if selected isotope is already in list. If 
                # so, add mass. Otherwise, create new Isotope and 
                # add to list
                if name in newMaterial.isotopes:
                    newMaterial.isotopes[name].mass += mass
                else:
                    newMaterial.isotopes[name] = Isotope(name,mass)
        else:
            newMaterial.isotopes[name] = Isotope(name, original_mass)
    return newMaterial


def writeData(filename, materials):
    """
    Write out all material data in the dictionary 'materials' to 'filename'.
    """

    fh = open(filename, "w")
    for cycle, time, mat in self.materials:
        fh.write("Cycle {0} Time {1} {2}\n".format(cycle, time, mat))
        material = self.materials[(cycle,time,mat)]
        for isotope in material.isotopes.values():
            fh.write("{0:7} {1:12.6e} kg\n".format(
                    str(isotope) + ":", isotope.mass))
        fh.write("\n")
    fh.close()
    return
