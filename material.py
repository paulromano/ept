#!/usr/bin/env python

"""
Class definition for a material
"""

import parameters

class Material():
    def __init__(self):
        """
        Create new instance of a material

        Attributes:
          isotopes = dictionary of form {"ZZAAAM": <Isotope instance>, ...}
          volume = volume of material

        Methods:
          mass() = mass of the material
          find(isotope) = Search for isotope by name
          heat() = heat content in W
          gammaHeat() = heat content due to photons in W
          neutronProduction() = neutron production rate in N/s
          externalDose() = external dose rate in Sv/hr at 1 meter
        """

        self.isotopes = {}
        self.volume = None

    def mass(self):
        """Return the total mass of the material in kg"""

        total_mass = 0
        for iso in self.isotopes.values():
            total_mass += iso.mass
        return total_mass

    def find(self, isotope):
        """
        Search through list of isotopes for one that matches a given name.
        If match found, return that Isotope. Otherwise return None.
        """

        for key in self.isotopes:
            if str(isotope).upper() == key.upper():
                return self.isotopes[key]
        return None

    def heat(self):
        """Return the heat content of the material in W"""

        rate = 0.0
        for key in self.isotopes:
            if key.upper() in parameters.data:
                isotope = self.isotopes[key]
                rate += isotope.mass * parameters.data[key.upper()][0]
        return rate

    def gammaHeat(self):
        """Return the heat content of the material due to photons in W"""

        rate = 0.0
        for key in self.isotopes:
            if key.upper() in parameters.data:
                isotope = self.isotopes[key]
                rate += isotope.mass * parameters.data[key.upper()][1]
        return rate

    def neutronProduction(self):
        """Return the photon heating rate of the material in N/s"""

        rate = 0.0
        for key in self.isotopes:
            if key.upper() in parameters.data:
                isotope = self.isotopes[key]
                rate += isotope.mass * parameters.data[key.upper()][2]
        return rate

    def externalDose(self):
        """
        Return the external dose rate of the material in Sv/hr at
        1-meter
        """

        rate = 0.0
        for key in self.isotopes:
            if key.upper() in parameters.data:
                isotope = self.isotopes[key]
                rate += isotope.mass * parameters.data[key.upper()][3]
        return rate
