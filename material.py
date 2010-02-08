#!/usr/bin/env python

"""
Class definition for a material
"""

class Material():
    def __init__(self):
        """
        Create new instance of a material
        """

        self.isotopes = {}

    def mass(self):
        """Return the total mass of the material"""

        total_mass = 0
        for iso in self.isotopes:
            total_mass += iso.mass
        return total_mass

#    def findIsotope(self, name):
#        """
#        Search through list of isotopes for one that matches a given name.
#        If match found, return that Isotope. Otherwise return None.
#        """
#
#        for index, isotope in enumerate(self.isotopes):
#            if str(isotope).upper() == name.upper():
#                return isotope
#        return None
