#!/usr/bin/env python

"""
Class definition for a material
"""

import parameters

class Material():
    def __init__(self):
        """
        Create new instance of a material

        isotopes = dictionary of form {"ZZAAAM": <Isotope instance>, ...}
        volume = volume of material
        """

        self.isotopes = {}
        self.volume = None

    def mass(self):
        """Return the total mass of the material"""

        total_mass = 0
        for iso in self.isotopes:
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

    def heatingRate(self):
        """Return the heating rate of the material in W/kg"""

        rate = 0.0
        for key in self.isotopes:
            if key.upper() in parameters.data:
                isotope = self.isotopes[key]
                rate += isotope.mass * parameters.data[key.upper()][0]
        return rate

    def gammaHeatingRate(self):
        """Return the photon heating rate of the material in W/kg"""

        rate = 0.0
        for key in self.isotopes:
            if key.upper() in parameters.data:
                isotope = self.isotopes[key]
                rate += isotope.mass * parameters.data[key.upper()][1]
        return rate

    def neutronRate(self):
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
