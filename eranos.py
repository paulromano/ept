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

from isotope import Isotope, FissionProduct
from material import Material
from cycle import Cycle
from fileIO import fileReSeek, fileReSeekList
from parameters import pf

def loadData(filename, parent=None, gui=True):
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
    
    # Determine default cooling period
    position = eranosFile.tell()
    m = fileReSeek(eranosFile, "^->COOLINGTIME\s+(\S+).*")
    if m:
        try:
            if m.groups()[0][:6] == "(PASSE":
                auto_cooling = True
            else:
                auto_cooling = False
                cooling_time = float(m.groups()[0])
        except:
            cooling_time = 30
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
        # Determine cooling period
        if auto_cooling:
            cooling_time = timestep*iterations*0.15/0.85
        cycles.append(Cycle(n, timestep, iterations, cooling_time))
    eranosFile.seek(0)

    # Determine how many materials to read total
    n_materials = 0
    for cycle in cycles:
        n_materials += len(cycle.times())*len(fuelNames)
    
    # Create progress bar
    if gui:
        progress = QProgressDialog("Loading ERANOS Data...",
                                   "Cancel", 0, n_materials, parent)
        progress.setWindowModality(Qt.WindowModal)
        progress.setWindowTitle("Loading...")
        progress.setMinimumDuration(0)
        progress.setValue(0)
        
    pValue = 0
    for cycle in cycles:
        print("Loading Cycle {0}...".format(cycle.n))

        # Determine critical mass
        fileReSeek(eranosFile, " ECCO6.*")
        xsDict = {}
        for i in fuelNames:
            m = fileReSeek(eranosFile, "\sREGION :(FUEL\d+|BLANK)\s*")
            name = m.groups()[0]
            m = fileReSeek(eranosFile,
                           "\s*TOTAL\s+(\S+)\s+(\S+)\s+\S+\s+(\S+).*")
            nuSigmaF = float(m.groups()[0])
            SigmaA = float(m.groups()[1])
            Diff = float(m.groups()[2])
            xsDict[name] = (nuSigmaF, SigmaA, Diff)

        # Find beginning of cycle
        m = fileReSeek(eranosFile, ".*M A T E R I A L   B A L A N C E.*")

        # Find TIME block and set time
        for node, time in enumerate(cycle.times()):
            # Progress bar
            if gui:
                QCoreApplication.processEvents()
                if (progress.wasCanceled()):
                    return None

            # Loop over fuel names
            for i in fuelNames:
                m = fileReSeek(eranosFile,"\s+MATERIAL\s(FUEL\d+|BLANK)\s+")
                name = m.groups()[0]
                volume = float(eranosFile.readline().split()[-1])
                for n in range(5): eranosFile.readline()
                # Read in material data
                material = readMaterial(eranosFile)
                material.volume = volume
                if time == 0:
                    material.nuFissionRate = xsDict[name][0]
                    material.absorptionRate = xsDict[name][1]
                    material.diffRate = xsDict[name][2]
                cycle.materials[(node,name)] = material
                # Set progress bar value
                pValue += 1
                if gui:
                    progress.setValue(pValue)
                #print((cycle.n, time, name)) # Only for debugging

        # Read uranium added/required feed
        for i in range(3):
            # Determine if there is additional mass or not enough
            regexList = [" 'REQUIRED FEED FOR FUEL (\d).*",
                         " 'ADDITIONAL FEED FOR FUEL (\d).*"]

            m, index = fileReSeekList(eranosFile,regexList)

            if index == 0:
                # We don't have enough fissile material
                cycle.extraMass = False
                mat = "FUEL{0}".format(m.groups()[0])
                m = fileReSeek(eranosFile," ->REPLMASS2\s+(\S+).*")
                cycle.requiredFeed += float(m.groups()[0])
                m = fileReSeek(eranosFile," ->REPLMASS1\s+(\S+).*")
                cycle.uraniumAdded[mat] = float(m.groups()[0])
            else:
                # Additional mass was produced
                cycle.extraMass = True
                mat = "FUEL{0}".format(m.groups()[0])
                m = fileReSeek(eranosFile," ->EXTRA\s+(\S+).*")
                cycle.additionalFeed[mat] = float(m.groups()[0])
                m = fileReSeek(eranosFile," ->REPLMASS\s+(\S+).*")
                cycle.uraniumAdded[mat] = float(m.groups()[0])

    # Create charge and discharge vectors based on additional/required
    # feed and uranium added values read in
    print("Creating charge/discharge vectors...")
    for cycle in cycles:
        cycle.discharge = Material()
        cycle.charge = Material()

        blank = cycle.materials[0,"BLANK"]
        if blank.isotopes["sfpU235"].mass < 1e-6:
            # Add blanket from previous cycle to discharge vector
            if cycle.n > 1:
                prevCycle = cycles[cycle.n - 2] # since n is indexed from 1
                time = len(prevCycle.times()) - 1
                prevBlank = prevCycle.materials[time, "BLANK"]
                for iso in prevBlank:
                    if type(iso) == FissionProduct:
                        prevCycle.discharge.addMass(str(iso), iso.mass, True)
                    else:
                        prevCycle.discharge.addMass(str(iso), iso.mass)
                prevCycle.discharge.expandFPs()

            # Add next blanket to charge vector
            for iso in blank:
                if type(iso) == FissionProduct:
                    cycle.charge.addMass(str(iso), iso.mass, True)
                else:
                    cycle.charge.addMass(str(iso), iso.mass)
            cycle.charge.expandFPs()

        for fuelName in cycle.uraniumAdded:
            time = len(cycle.times()) - 1
            mat = cycle.materials[time, fuelName]
            
            # Add depleted uranium to charge
            total_removed = cycle.uraniumAdded[fuelName]
            cycle.charge.addMass("U235", 0.002*total_removed)
            cycle.charge.addMass("U238", 0.998*total_removed)

            # Add fission products to discharge
            total_fp_mass = sum([fp.mass for fp in mat.fissionProducts()])
            for fp in mat.fissionProducts():
                fpMass = total_removed*fp.mass/total_fp_mass
                cycle.discharge.addMass(fp.name, fpMass, True)

        # Expand FPs in discharge vector
        cycle.discharge.expandFPs()

        if cycle.extraMass:
            # Add extra actinides to discharge vector
            for fuelName in cycle.additionalFeed:
                time = len(cycle.times()) - 1
                mat = cycle.materials[time, fuelName]

                extra_mass = cycle.additionalFeed[fuelName]

                # determine total mass of actinides
                total_ac_mass = 0
                for iso in mat:
                    if type(iso) == Isotope:
                        total_ac_mass += iso.mass

                # add to discharge vector
                for iso in mat:
                    if type(iso) == Isotope:
                        acMass = extra_mass * iso.mass/total_ac_mass
                        cycle.discharge.addMass(str(iso), acMass)

        else:

            # Add minor actinides to charge vector
            for name, frac in [("Np237", 0.0588), ("Pu238", 0.0271),
                               ("Pu239", 0.4905), ("Pu240", 0.2400),
                               ("Pu241", 0.1092), ("Pu242", 0.0744)]:
                cycle.charge.addMass(name, frac*cycle.requiredFeed)
    
    try:
        # Determine reaction rates for FUEL3, FUEL6, FUEL9, and
        # BLANK. First we need to load material balance data. Is this
        # just reading the same data as the last timestep of the last
        # cycle???
        n = len(cycles) + 1
        cycle = Cycle(n, 0, 0, 0)
        cycles.append(cycle)
        for i in fuelNames:
            m = fileReSeek(eranosFile,"\s+MATERIAL\s(FUEL\d+|BLANK)\s+")
            name = m.groups()[0]
            volume = float(eranosFile.readline().split()[-1])
            for n in range(5): eranosFile.readline()
            # Read in material data
            material = readMaterial(eranosFile)
            material.volume = volume
            cycle.materials[(0,name)] = material

        # Now read fission, absorption, and diffusion rates to be able to
        # determine the critical mass
        fuelNames = ['FUEL3', 'FUEL6', 'FUEL9', 'BLANK']
        fileReSeek(eranosFile, " ECCO6.*")
        for name in fuelNames:
            m = fileReSeek(eranosFile, "\sREGION :(FUEL\d+|BLANK)\s*")
            name = m.groups()[0]
            m = fileReSeek(eranosFile,
                           "\s*TOTAL\s+(\S+)\s+(\S+)\s+\S+\s+(\S+).*")
            cycle.materials[(0,name)].nuFissionRate = float(m.groups()[0])
            cycle.materials[(0,name)].absorptionRate = float(m.groups()[1])
            cycle.materials[(0,name)].diffRate = float(m.groups()[2])
    except:
        # No ECCO calculation at end?
        print('WARNING: No ECCO_BLANK calculation at end of run?')

    # Create progress bar
    if gui:
        progress = QProgressDialog("Expanding fission products...",
                                   "Cancel", 0, n_materials, parent)
        progress.setWindowModality(Qt.WindowModal)
        progress.setWindowTitle("Loading...")
        progress.setMinimumDuration(0)
        progress.setValue(0)
        
    pValue = 0
    # Expand all fission products
    for cycle in cycles:
        # Progress bar
        if gui:
            QCoreApplication.processEvents()
            if (progress.wasCanceled()):
                return None

        print("Expanding fission products for Cycle {0}...".format(cycle.n))
        for mat in cycle.materials.values():
            mat.expandFPs()

            # Set progress bar value
            pValue += 1
            if gui:
                progress.setValue(pValue)


    # Close file and return
    eranosFile.close()
    return cycles
                
def readMaterial(fh):
    """
    Read in material data on fh starting from first line (usually Na23)
    of data and return it in a Material instance.
    """

    mat = Material()
    while True:
        words = fh.readline().split()
        if len(words) == 1: break
        name = words[1]
        if name == "Am242g":
            name = "Am242"
        original_mass = float(words[3])
        if name[0:3] == "sfp":
            mat.isotopes[name] = FissionProduct(name,original_mass)
        else:
            mat.isotopes[name] = Isotope(name, original_mass)
    return mat


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
        for node, time in enumerate(cycle.times()):
            for name in materialNames:
                fh.write("Cycle {0} Time {1} {2}\n".format(
                        cycle.n, time, name))
                material = cycle.materials[(node,name)]
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
                fh.write("    Charlton: DOE Attrativeness (u1) = {0}\n".format(
                        material.charlton1()))
                fh.write("    Charlton: Pu Heating Rate (u2) = {0}\n".format(
                        material.charlton2()))
                fh.write("    Charlton: Weight Fraction of Even Pu (u3) = {0}\n".format(
                        material.charlton3()))
                fh.write("    Charlton: Concentration (u4) = {0}\n".format(
                        material.charlton4()))
                fh.write("    Charlton: Dose Rates (u5) = {0}\n".format(
                        material.charlton5()))
                fh.write("    Bathke: Sub-national (FOM1) = {0}\n".format(
                        material.bathke1()))
                fh.write("    Bathke: Unadvanced Nation (FOM2) = {0}\n".format(
                        material.bathke2()))
                for isotope in material.isotopes.values():
                    fh.write("    {0:7} {1:12.6e} kg\n".format(
                            str(isotope) + ":", isotope.mass))
                fh.write("\n")
    fh.close()
    return
