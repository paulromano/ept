#!/usr/bin/env python

"""
Class definition for a material
"""

import parameters
import math

class Material():
    def __init__(self):
        """
        Create new instance of a material

        Attributes:
          isotopes = dictionary of form {"ZZAAAM": <Isotope instance>, ...}
          volume = volume of material
          nuFissionRate = nuFission cross section * flux
          absorptionRate = absorption cross section * flux
          diffRate = diffusion coefficient * flux

        Methods:
          mass() = mass of the material
          find(isotope) = Search for isotope by name
          heat() = heat content in W
          gammaHeat() = heat content due to photons in W
          neutronProduction() = neutron production rate in N/s
          externalDose() = external dose rate in Sv/hr at 1 meter
          criticalMass() = critical mass of bare sphere in kg
        """

        self.isotopes = {}
        self.volume = None
        self.nuFissionRate = None
        self.absorptionRate = None
        self.diffRate = None

    def mass(self, Actinide = False, Fissile = False):
        """
        Return the total mass of the material in kg

        If the Actinide argument is True, only includes isotopes that
        are actinides

        If the Fissile argument is True, only includes isotopes that
        are fissile
        """

        total_mass = 0
        for isotope in self.isotopes.values():
            if Actinide and not isotope.isActinide():
                continue
            if Fissile and not isotope.isFissile():
                continue
            total_mass += isotope.mass
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

    def heat(self, MA = False):
        """Return the heat content of the material in W"""

        rate = 0.0
        for key in self.isotopes:
            if key.upper() in parameters.data:
                isotope = self.isotopes[key]
                if not MA or isotope.isMinorActinide():
                    rate += isotope.mass * parameters.data[key.upper()][0]
        return rate

    def gammaHeat(self, MA = False):
        """Return the heat content of the material due to photons in W"""

        rate = 0.0
        for key in self.isotopes:
            if key.upper() in parameters.data:
                isotope = self.isotopes[key]
                if not MA or isotope.isMinorActinide():
                    rate += isotope.mass * parameters.data[key.upper()][1]
        return rate

    def neutronProduction(self, MA = False):
        """Return the photon heating rate of the material in N/s"""

        rate = 0.0
        for key in self.isotopes:
            if key.upper() in parameters.data:
                isotope = self.isotopes[key]
                if not MA or isotope.isMinorActinide():
                    rate += isotope.mass * parameters.data[key.upper()][2]
        return rate

    def externalDose(self, MA = False):
        """
        Return the external dose rate of the material in Sv/hr at
        1-meter
        """

        rate = 0.0
        for key in self.isotopes:
            if key.upper() in parameters.data:
                isotope = self.isotopes[key]
                if not MA or isotope.isMinorActinide():
                    rate += isotope.mass * parameters.data[key.upper()][3]
        return rate

    def criticalMass(self):
        """
        Returns the critical mass of bare sphere of the material 
        in kg

        To determine the critical mass, we merely need to set the
        geometric buckling equal to the material buckling:

           (pi/R)^2 = (nuSigmaF*phi - SigmaA*phi)/(D*phi)

        The nuFission, absorption, and diffusion coefficient reaction
        rates are found in the output of an ECCO calculation. We can 
        thus solve for the critical radius as:

           R = sqrt( pi^2*D*phi / (nuSigmaF*phi - SigmaA*phi) )

        Then we multiply the volume of a sphere of radius R by the
        density of the material to determine the critical mass.
        """

        if self.nuFissionRate > self.absorptionRate:
            R = math.sqrt(math.pi**2 * self.diffRate/
                          (self.nuFissionRate - self.absorptionRate))
            return 4./3. * math.pi * R**3 * self.mass()/self.volume
        return None

