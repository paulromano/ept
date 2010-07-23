#!/usr/bin/env python

"""
Class definition for a cycle
"""

class Cycle():
    def __init__(self, n, timestep, iterations, cooling_time=None):
        """
        Create new instance of a cycle

        n = cycle number
        timestep = cycle timestep in days
        iterations = number of timesteps

        materials is a dictionary of the form:
            {(timenode, material): <Material instance>, ...}
        """

        # Set cycle attributes
        self.n = n
        self.timestep = timestep
        self.iterations = iterations
        self.cooling_time = cooling_time
        self.materials = {}

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

