#!/usr/bin/env python

"""
Class definition for a cycle
"""

class Cycle():
    """
    Create new instance of a cycle

    Attributes:
      n = cycle number
      timestep = cycle timestep in days
      iterations = number of timesteps
      
      materials is a dictionary of the form:
        {(timenode, material): <Material instance>, ...}
    """


    def __init__(self, n, timestep, iterations, cooling_time=None):
        # Set cycle attributes
        self.n = n
        self.timestep = timestep
        self.iterations = iterations
        self.cooling_time = cooling_time
        self.materials = {}

        self.requiredFeed = 0
        self.uraniumAdded = {}
        self.additionalFeed = {}
        self.dpa = {}
        self.power = {}

    def times(self):
        """
        Return a list of all the timesteps in days including the step
        for cooling if applicable.
        """

        timeList = [self.timestep*i for i in range(self.iterations+1)]
        if self.cooling_time:
            timeList.append(timeList[-1] + self.cooling_time)
        return timeList

    def materialNames(self):
        """
        Returns a sorted list of the materials.
        """

        nameList = []
        for time, name in self.materials:
            if not name in nameList:
                nameList.append(name)
        nameList.sort()
        return nameList

