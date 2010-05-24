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
from cycle import Cycle
from fileIO import fileReSeek

def loadData(filename, parent=None):
    """
    Loads material data from an ERANOS output file.

    Returns a list 'cycles' with all the Cycle instances.
    """

    # Open file
    eranosFile = open(filename, "r")
    cycles = []

    # Find the names of all the fuel regions
    fuelNames = []
    m = fileReSeek(eranosFile, "^->LISTE_MILIEUX.*")
    fuelNames += re.findall("'(FUEL\d+)'", m.group())
    while True:
        line = eranosFile.readline().strip()
        fuelNames += re.findall("'(FUEL\d+)'", line)
        if line[-1] == ";": break

    # Determine if there is a blanket material
    m = fileReSeek(eranosFile, "^->BLANKET.*")
    if m:
        fuelNames += ["BLANK"]
    else:
        eranosFile.seek(0)
    
    # Determine cooling period
    position = eranosFile.tell()
    m = fileReSeek(eranosFile, "^->COOLING\s+(\d+).*")
    if m:
        cooling_time = eval(m.groups()[0])
    else:
        cooling_time = None
        eranosFile.seek(position)

    # Determine cycle information
    while True:
        m = fileReSeek(eranosFile, ".*->CYCLE\s+(\d+).*")
        if not m: break
        n = int(m.groups()[0])
        m = fileReSeek(eranosFile, "^->PASSE\s\((\d+)\).*")
        if not m: break
        timestep = int(m.groups()[0])
        m = fileReSeek(eranosFile, "^->ITER\s(\d+).*")
        iterations = int(m.groups()[0])
        cycles.append(Cycle(n, timestep, iterations, cooling_time))
    eranosFile.seek(0)

    # Determine how many materials to read total
    n_materials = 0
    for cycle in cycles:
        n_materials += len(cycle.times())*len(fuelNames)
    
    # Create progress bar
    progress = QProgressDialog("Loading ERANOS Data...",
                               "Cancel", 0, n_materials, parent)
    progress.setWindowModality(Qt.WindowModal)
    progress.setMinimumDuration(0)
    progress.setValue(0)

    pValue = 0
    for cycle in cycles:
        # Find beginning of cycle
        m = fileReSeek(eranosFile, "\s*'MASS BALANCE OF CYCLE (\d+)'\s*")

        # Find TIME block and set time
        for time in cycle.times():
            # Progress bar
            QCoreApplication.processEvents()
            if (progress.wasCanceled()):
                return None

            # Loop over fuel names
            for i in fuelNames:
                m = fileReSeek(eranosFile,"\s+MATERIAL\s(FUEL\d+|BLANK)\s+")
                name = m.groups()[0]
                volume = eval(eranosFile.readline().split()[-1])
                for n in range(5): eranosFile.readline()
                # Read in material data
                material = readMaterial(eranosFile)
                material.volume = volume
                cycle.materials[(time,name)] = material
                # Set progress bar value
                pValue += 1
                progress.setValue(pValue)
                #print((cycle.n, time, name)) # Only for debugging

    eranosFile.close()
    return cycles
           
                
def readMaterial(fh):
    """
    Read in material data on fh starting from first line (usually Na23)
    of data and return it in a Material instance.
    """

    # TODO: Change this so that sfp.csv is only opened once and data
    #       is stored in memory

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


def writeData(filename, cycles):
    """
    Write out all material data in the 'cycles' list to 'filename'.
    """

    # Open file for writing
    fh = open(filename, "w")

    # Write material and cycle information
    materialNames = cycles[0].materialNames()
    fh.write("Materials:\n")
    for name in materialNames:
        fh.write("    {0}\n".format(name))
    fh.write("\n")
    for cycle in cycles:
        fh.write("Cycle {0}: {1}\n".format(
                cycle.n, " ".join([str(i) for i in cycle.times()])))
    fh.write("\n")

    # Write data from materials dictionary
    for cycle in cycles:
        for time in cycle.times():
            for name in materialNames:
                fh.write("Cycle {0} Time {1} {2}\n".format(
                        cycle.n, time, name))
                material = cycle.materials[(time,name)]
                fh.write("    Volume = {0}\n".format(material.volume))
                fh.write("    Heating Rate = {0} W/kg\n".format(
                        material.heatingRate()))
                for isotope in material.isotopes.values():
                    fh.write("    {0:7} {1:12.6e} kg\n".format(
                            str(isotope) + ":", isotope.mass))
                fh.write("\n")
    fh.close()
    return
