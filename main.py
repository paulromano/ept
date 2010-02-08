#!/usr/bin/env python

"""
Copyright (C) 2010 Paul K. Romano

Code to process mass output data from ERANOS and rewrite it in a
form that VISION can use.
"""

from __future__ import division
import os
import re
import textwrap
import csv
import pdb

from isotope import Isotope
from material import Material

__version__ = "0.1.1"

def main():
    """Main logic for ERANOS output processing"""

    # Parse command line options
    from optparse import OptionParser
    usage = "usage: %prog [options] file"
    version = "ERANOS Processing Tool v{0}".format(__version__)
    p = OptionParser(usage=usage, version=version)
    (options, args) = p.parse_args()
    if not args:
        p.print_help()
        return
    filename = args[0]
    # Return error if specified output file doesn't exist
    if not os.path.isfile(filename):
        print("Error: file '{0}' does not exist!".format(filename))
        return 1


    # Open file
    fh = open(filename, "r")

    # Find the names of all the fuel regions
    fuelNames = []
    m = fileReSeek(fh, "^->LISTE_MILIEUX.*")
    fuelNames += re.findall("'(FUEL\d+)'", m.group())
    while True:
        line = fh.readline().strip()
        fuelNames += re.findall("'(FUEL\d+)'", line)
        if line[-1] == ";": break
    # TODO: Display list of fuel materials

    # Determine number of cycles
    n_cycles = 0
    while True:
        m = fileReSeek(fh, ".*->CYCLE\s+(\d+).*")
        if not m: break
        n = int(m.groups()[0])
        if n > n_cycles:
            n_cycles = n
    fh.seek(0)

    allMaterials = {}
    for cycle in range(1, n_cycles + 1):

        # Find beginning of cycle
        m = fileReSeek(fh, "\s*'MASS BALANCE OF CYCLE (\d+)'\s*")

        while True:
            # Find TIME block and set time
            m = fileReSeek(fh, "\s*->TIME\s+(\d+)\s*")
            if not m: break
            time = m.groups()[0]

            # Read isotope data and create new material
            # Loop over fuel names
            for i in fuelNames:
                m = fileReSeek(fh,"\s+MATERIAL\s(FUEL\d+)\s+")
                mat = m.groups()[0]
                print("Cycle {0} Time {1} {2}".format(cycle, time, mat))
                for n in range(6): fh.readline()
                fuel = Material()
                allMaterials[(cycle,time,mat)] = fuel
                # Loop over individual isotopes
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
                            if name in fuel.isotopes:
                                fuel.isotopes[name].mass += mass
                            else:
                                fuel.isotopes[name] = Isotope(name,mass)
                    else:
                        fuel.isotopes[name] = Isotope(name, original_mass)
                for iso in fuel.isotopes.values():
                    print("{0:7} {1:12.6e} kg".format(str(iso) + ":", iso.mass))
                print("")
            
            # Find position of next TIME block
            position = fh.tell()
            m = fileReSeek(fh, "\s*->TIME\s+(\d+)\s*")
            timePosition = fh.tell()
            fh.seek(position)
            
            # Find position of next CYCLE block
            m = fileReSeek(fh, "\s*'MASS BALANCE OF CYCLE (\d+)'\s*")
            cyclePosition = fh.tell()
            
            # If cycle block is first, break out of reading TIME blocks
            if cyclePosition < timePosition:
                fh.seek(position)
                break
            fh.seek(position)
            
        
                
def fileReSeek(fh, regex):
    """
    Seek to a position in the file open on handle fh that matches
    the regular expression regex and return a MatchObject. If no
    match is found, return None.
    """

    p = re.compile(regex)
    while True:
        line = fh.readline()
        if line == '':
            return None
        match = p.match(line)
        if match:
            return match


if __name__ == "__main__":
    main()
