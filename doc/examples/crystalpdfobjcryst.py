#!/usr/bin/env python
########################################################################
#
# diffpy.srfit      by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2008 Trustees of the Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Chris Farrow
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
########################################################################
"""Example of using ProfileGenerators in FitContributions.

This is an example of building a ProfileGenerator and using it in a
FitContribution in order to fit theoretical intensity data.

The IntensityGenerator class is an example of a ProfileGenerator that can be
used by a FitContribution to help generate a signal.

The makeRecipe function shows how to build a FitRecipe that uses the
IntensityGenerator.

"""

import os

import numpy

from pyobjcryst.crystal import Crystal
from pyobjcryst.atom import Atom
from pyobjcryst.scatteringpower import ScatteringPowerAtom

from diffpy.srfit.pdf import PDFGenerator
from diffpy.srfit.fitbase import Profile
from diffpy.srfit.fitbase import FitContribution, FitRecipe
from diffpy.srfit.fitbase import FitResults
from diffpy.srfit.structure.diffpystructure import StructureParSet

from gaussianrecipe import scipyOptimize, parkOptimize

def makeNi():

    sp = ScatteringPowerAtom("Ni", "Ni")
    sp.Biso = 8*numpy.pi**2*0.003
    #sp.B11 = sp.B22 = sp.B33 = 8*numpy.pi**2*0.003
    atom = Atom(0, 0, 0, "Ni", sp)

    crystal = Crystal(3.52, 3.52, 3.52, "225")
    crystal.AddScatterer(atom)

    return crystal

####### Example Code

def makeRecipe(datname):
    """Create a recipe that uses the IntensityGenerator.

    This will create a FitContribution that uses the IntensityGenerator,
    associate this with a Profile, and use this to define a FitRecipe.

    """

    ## The Profile
    profile = Profile()

    # Load data and add it to the profile
    x, y, junk, u = numpy.loadtxt(datname, unpack=True)
    profile.setObservedProfile(x, y, u)
    profile.setCalculationRange(0, 20, 0.05)

    ## The ProfileGenerator
    generator = PDFGenerator("G")
    stru = makeNi()
    generator.setPhase(stru)
    generator.setQmax(40.0)
    
    ## The FitContribution
    contribution = FitContribution("nickel")
    contribution.addProfileGenerator(generator)
    contribution.setProfile(profile, xname = "r")

    # Make the FitRecipe and add the FitContribution.
    recipe = FitRecipe()
    recipe.addContribution(contribution)

    phase = generator.phase

    recipe.addVar(generator.scale, 1)
    recipe.addVar(generator.qdamp, 0.01)
    recipe.addVar(generator.delta2, 5)
    lattice = phase.getLattice()
    recipe.addVar(lattice.a)
    # We don't need to constrain 'b' and 'c', this is already done for us,
    # consistent with the space group of the crystal.

    Biso = recipe.newVar("Biso")
    for scatterer in phase.getScatterers():
        recipe.constrain(scatterer.Biso, Biso)

    # Give the recipe away so it can be used!
    return recipe

def plotResults(recipe):
    """Plot the results contained within a refined FitRecipe."""

    # All this should be pretty familiar by now.
    names = recipe.getNames()
    vals = recipe.getValues()

    r = recipe.nickel.profile.x

    g = recipe.nickel.profile.y
    gcalc = recipe.nickel.profile.ycalc
    diff = g - gcalc - 0.5 * max(g)

    import pylab
    pylab.plot(r,g,'bo',label="G(r) Data")
    pylab.plot(r, gcalc,'r-',label="G(r) Fit")
    pylab.plot(r,diff,'g-',label="G(r) diff")
    pylab.xlabel("$r (\AA)$")
    pylab.ylabel("$G (\AA^{-2})$")
    pylab.legend(loc=1)

    pylab.show()
    return

if __name__ == "__main__":

    # Make the data and the recipe
    data = "data/ni.dat"

    # Make the recipe
    recipe = makeRecipe(data)

    # Optimize
    scipyOptimize(recipe)
    #parkOptimize(recipe)

    # Generate and print the FitResults
    res = FitResults(recipe)
    res.printResults()

    # Plot!
    plotResults(recipe)

# End of file