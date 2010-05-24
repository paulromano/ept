#!/usr/bin/env python

"""
Copyright (C) 2010 Paul K. Romano

Code to process mass output data from ERANOS and rewrite it in a
form that VISION can use.
"""

from __future__ import division, print_function
import re
import math

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from isotope import Isotope
from material import Material
from cycle import Cycle
from fileIO import fileReSeek
from parameters import sfp

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
        # Determine critical mass
        xsDict = {}
        for i in fuelNames:
            m = fileReSeek(eranosFile, "\sREGION :(FUEL\d+|BLANK)\s*")
            name = m.groups()[0]
            m = fileReSeek(eranosFile,
                           "\s*TOTAL\s+(\S+)\s+(\S+)\s+\S+\s+(\S+).*")
            nuSigmaF = eval(m.groups()[0])
            SigmaA = eval(m.groups()[1])
            Diff = eval(m.groups()[2])
            xsDict[name] = (nuSigmaF, SigmaA, Diff)

        # Find beginning of cycle
        m = fileReSeek(eranosFile, ".*M A T E R I A L   B A L A N C E.*")

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
                if time == 0:
                    material.nuFissionRate = xsDict[name][0]
                    material.absorptionRate = xsDict[name][1]
                    material.diffRate = xsDict[name][2]
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
            for nrow, row in enumerate(sfp):
                if nrow == 0:
                    # Determine which column to use
                    column = [i.upper() for i in row].index(name)
                    continue
                if nrow > 0:
                    name = row[0]
                    fraction = row[column]
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
    # TODO: encapsulate some of this logic in a Material object method?
    for cycle in cycles:
        for time in cycle.times():
            for name in materialNames:
                fh.write("Cycle {0} Time {1} {2}\n".format(
                        cycle.n, time, name))
                material = cycle.materials[(time,name)]
                fh.write("    Volume = {0}\n".format(material.volume))
                fh.write("    Heating Rate = {0} W/kg\n".format(
                        material.heat()/material.mass()))
                fh.write("    Photon Heating Rate = {0} W/kg\n".format(
                        material.gammaHeat()/material.mass()))
                fh.write("    Neutron Production Rate = {0} N/s/kg\n".format(
                        material.neutronProduction()/material.mass()))
                fh.write("    External Dose Rate = {0} Sv/hr/kg at 1 m\n".format(
                        material.externalDose()/material.mass()))
                fh.write("    Critical Mass = {0} kg\n".format(
                        material.criticalMass()))
                for isotope in material.isotopes.values():
                    fh.write("    {0:7} {1:12.6e} kg\n".format(
                            str(isotope) + ":", isotope.mass))
                fh.write("\n")
    fh.close()
    return
