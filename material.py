#!/usr/bin/env python

"""
Class definition for a material
"""

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
            if key.upper() in heatRateData:
                isotope = self.isotopes[key]
                rate += isotope.mass * heatRateData[key.upper()] * 1e-3
        return rate


heatRateData = {"TL207": 559277.91,
                "TL208": 6929936.6,
                "TL209": 6794956.82,
                "PB209": 5225.94,
                "PB210": 0.02,
                "PB211": 73970.16,
                "PB212": 2645.98,
                "PB214": 104571.75,
                "BI210": 286.15,
                "BI210M": 0,
                "BI211": 16689972.66,
                "BI212": 249138.55,
                "BI213": 81310.97,
                "BI214": 565863.93,
                "PO210": 144.02,
                "PO211": 4297958919.57,
                "PO212": 9.40E+015,
                "PO213": 638083469206932,
                "PO214": 14900188063027.2,
                "PO215": 1316067020441.46,
                "PO216": 14255309890.72,
                "PO218": 10248864.32,
                "AT217": 68692611710.04,
                "RN218": 63622860131.49,
                "RN219": 539709229.8,
                "RN220": 35029245.09,
                "RN222": 5097.21,
                "FR221": 6842257.01,
                "FR223": 100445.43,
                "RA222": 52956124.36,
                "RA223": 1823.52,
                "RA224": 5466.87,
                "RA225": 27.49,
                "RA226": 0.03,
                "RA228": 0.02,
                "AC225": 2027.49,
                "AC227": 0.04,
                "AC228": 19380.21,
                "TH226": 1026309.95,
                "TH227": 1121.93,
                "TH228": 26.8,
                "TH229": 0.01,
                "TH230": 0,
                "TH231": 298.32,
                "TH232": 0,
                "TH233": 92425.61,
                "TH234": 9.39,
                "PA231": 0,
                "PA232": 2808.79,
                "PA233": 47.11,
                "PA234": 28713.9,
                "PA234M": 3394336.84,
                "PA235": 92708.37,
                "U230": 969.37,
                "U231": 111.29,
                "U232": 0.69,
                "U233": 0,
                "U234": 0,
                "U235": 0,
                "U236": 0,
                "U237": 154.51,
                "U238": 0,
                "U239": 89994.2,
                "U240": 760.05,
                "NP235": 0.08,
                "NP236": 0,
                "NP236M": 466.35,
                "NP237": 0,
                "NP238": 1241.49,
                "NP239": 560.74,
                "NP240": 127735.49,
                "NP240M": 613508.7,
                "NP241": 136147.27,
                "PU236": 18.49,
                "PU237": 4.45,
                "PU238": 0.57,
                "PU239": 0,
                "PU240": 0.01,
                "PU241": 0,
                "PU242": 0,
                "PU243": 3003.44,
                "PU244": 0,
                "PU245": 2860.73,
                "PU246": 41.18,
                "AM241": 0.11,
                "AM242": 917.75,
                "AM242M": 0,
                "AM243": 0.01,
                "AM244": 6662.75,
                "AM244M": 89656.12,
                "AM245": 11465.05,
                "AM246": 246857.22,
                "CM241": 61.85,
                "CM242": 121.84,
                "CM243": 1.89,
                "CM244": 2.83,
                "CM245": 0.01,
                "CM246": 0.01,
                "CM247": 0,
                "CM248": 0,
                "CM249": 20489.83,
                "CM250": 0.06,
                "BK249": 1.21,
                "BK250": 27026.72,
                "BK251": 85711.79,
                "CF249": 0.19,
                "CF250": 4.06,
                "CF251": 0.06,
                "CF252": 38.38,
                "CF253": 16.8,
                "CF254": 10043.91,
                "ES253": 14.62,
                "ES254": 73.21,
                "ES255": 573.63}
            
