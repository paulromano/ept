#!/usr/bin/env python

"""
Class definition for a material
"""

from isotope import Isotope, FissionProduct
import parameters
import math

class Material():
    """
    Create new instance of a material
    
    Attributes:
      isotopes = dictionary of form {"ZZAAAM": <Isotope instance>, ...}
      volume = volume of material
      nuFissionRate = nuFission cross section * flux
      absorptionRate = absorption cross section * flux
      diffRate = diffusion coefficient * flux
      flux = total flux
      power = 
      
    Methods:
      mass() = mass of the material
      SQ() = significant quantities of material
      find(isotope) = Search for isotope by name
      heat() = heat content in W
      gammaHeat() = heat content due to photons in W
      neutronProduction() = neutron production rate in N/s
      externalDose() = external dose rate in Sv/hr at 1 meter
      criticalMass() = critical mass of bare sphere in kg
      addMass() = add mass of a specified isotope

      bathke1()
      bathke2()
      charlton1()
      charlton2()
      charlton3()
      charlton4()
      charlton5()
    """

    def __init__(self):
        self.isotopes = {}
        self.volume = None
        self.nuFissionRate = None
        self.absorptionRate = None
        self.diffRate = None
        self.flux = None
        self.power = None
        self.dpa = None

    def addMass(self, name, mass, FP=False):
        """Check if selected isotope is already in list. If so, add
        mass. Otherwise, create new Isotope and add to list
        """

        if name in self.isotopes:
            self.isotopes[name].mass += mass
        else:
            if FP:
                self.isotopes[name] = FissionProduct(name, mass)
            else:
                self.isotopes[name] = Isotope(name, mass)

    def __iter__(self):
        for iso in self.isotopes.values():
            yield iso

    def expandFPs(self):
        for fp in self.fissionProducts():
            # Record name/mass and delete FP
            name = fp.name
            original_mass = fp.mass
            del self.isotopes[name]

            # Expand into isotopes
            name = name[3:].upper()
            if name == "AM242":
                name = "AM242M"
            for nrow, row in enumerate(parameters.pf):
                if nrow == 0:
                    # Determine which column to use
                    column = row.index(name)
                    continue
                if nrow > 0:
                    name = row[0]
                    fraction = row[column]
                    mass = original_mass*fraction
                    if name == "Cs133":
		      print(name,original_mass,fraction,fp.name)
		      raw_input('Press ENTER to continue...\n')
                self.addMass(name, mass)

    def fissionProducts(self):
        for iso in self.isotopes.values():
            if type(iso) == FissionProduct:
                yield iso

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

    def SQ(self):
        """
        Return the number of 'significant quantities' (SQs) in the
        material
        """

        massPu = 0.0
        massNp = 0.0
        massU  = 0.0
        for isotope in self.isotopes.values():
            if isotope.Z == 94:
                massPu += isotope.mass
            elif str(isotope) == "Np237":
                massNp += isotope.mass
            elif isotope.Z == 92:
                massU += isotope.mass
        return massPu/8.0 + massNp/25.0 + massU/75.0

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
        """Return the neutron production rate of the material in N/s"""

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
         #   R = math.sqrt(math.pi**2 * self.diffRate/
         #                 (self.nuFissionRate - self.absorptionRate))
            R = math.sqrt(math.pi**2 * (self.flux * 0.45)/
                          (self.nuFissionRate - self.absorptionRate))
            return 4./3. * math.pi * R**3 * 16. / 1000. #self.mass()/self.volume
        return None

    def dpavalue(self):
        if self.dpa is not None:
           dpavalue = self.dpa
        else:
	   dpavalue = 0.
        return dpavalue

    def intpower(self):
        if self.power is not None:
	   intpower = self.power/1.E6
	else:
	   intpower = 0.
	return intpower

    def bathke1(self, Dose = False):
        """
        Returns the first metric in the GLOBAL '09 paper, The
        Attractiveness of Materials in Advanced Nuclear Fuel Cycles
        for Various Proliferation and Theft Scenarios
        """

        M = self.criticalMass()
        if not M:
            return None
        h = self.heat(True)/self.mass()
        # Convert dose to rad (assume 1 rad = 1 rem)
        if not Dose:
            D = 0.2 * 100 * self.externalDose()
        else:
            D = 0.
        print (M,h,D)
        return 1.0 - math.log10(M/800.0 + M*h/4500.0 + M/50.0 * 
                                (D/500.0)**(1.0/math.log10(2.0)))

    def bathke2(self, Dose = False):
        """
        Returns the second metric in the GLOBAL '09 paper, The
        Attractiveness of Materials in Advanced Nuclear Fuel Cycles
        for Various Proliferation and Theft Scenarios
        """

        M = self.criticalMass()
        if not M:
            return None
        h = self.heat()/self.mass()
        S = self.neutronProduction()/self.mass()
        # Convert dose to rad (assume 1 rad = 1 rem)
        if not Dose:
            D = 0.2 * 100 * self.externalDose()
        else:
            D = 0.
        return 1.0 - math.log10(M/800.0 + M*h/4500.0 + M*S/6.8e6 + 
                                M/50.0 * (D/500.0)**(1.0/math.log10(2.0)))

    def charlton1(self):
        """
        Determine u_1 from Charlton et al.

        The attractiveness level of the fuel being analyzed is always
        'C' so we just need to determine which category the fuel is
        in based on the Pu+U233 mass.
        """

        massPuU233 = 0
        massU235 = 0
        for isotope in self.isotopes.values():
            if isotope.Z == 94 or str(isotope) == "U233":
                massPuU233 += isotope.mass
            if str(isotope) == "U235":
                massU235 += isotope.mass

        # Evaluate Pu/U233 Category
        if massPuU233 < 0.4:
            u = 0.45 # Category IV
        elif massPuU233 >= 0.4 and massPuU233 < 2:
            u = 0.35 # Category III
        elif massPuU233 >= 2 and massPuU233 <6:
            u = 0.25 # Category II
        else:
            u = 0.15 # Category I

        # Evaluate U235 Category
        if massU235 < 2:
            u_ = 0.45 # Category IV
        elif massU235 >= 2 and massU235 < 6:
            u_ = 0.35 # Category III
        elif massU235 >= 6 and massU235 < 20:
            u_ = 0.25 # Category II
        else:
            u_ = 0.15 # Category I

        # Choose lowest category
        return min(u,u_)

    def charlton2(self):
        """
        Determine u_2 from Charlton et al.
        """

        rate = 0.0
        mass = 0.0
        for key in self.isotopes:
            if key.upper() in parameters.data:
                isotope = self.isotopes[key]
                if isotope.Z == 94:
                    rate += isotope.mass * parameters.data[key.upper()][0]
                    mass += isotope.mass
        x = rate/mass
        return 1 - math.exp(-3.0*(x/570.0)**0.8)

    def charlton3(self):
        """
        Determine u_3 from Charlton et al.
        """

        evenMass = 0
        totalMass = 0
        for isotope in self.isotopes.values():
            if isotope.Z == 94:
                totalMass += isotope.mass
                if isotope.A % 2 == 0:
                    evenMass += isotope.mass
        if totalMass > 0:
            x = evenMass / totalMass
        else:
            x = 0
        return 1 - math.exp(-3.5*x**1.8)

    def charlton4(self):
        """
        Determine u_4 from Charlton et al.
        """

        x = self.SQ() / self.mass() * 1000
        if x < 0.01:
            return 1
        else:
            return math.exp(-2.5*(x/125.0))

    def charlton5(self):
        """
        Determine u_5 from Charlton et al.
        """

        x = 100 * self.externalDose() / self.SQ()
        if x <= 0.2:
            return 0
        elif x > 0.2 and x <= 5:
            return 0.0520833*x - 0.010416
        elif x > 5 and x <= 75:
            return 0.0035714*x + 0.232143
        elif x > 75 and x <= 600:
            return 0.00095238*x + 0.428571
        else:
            return 1

