#!/usr/bin/env python

from diffpy.srfit.fit.functions import array, maximum

__all__ = ["restrain"]

def restrain(eq, lb, ub = None, sig = 1):
    """Restrain an equation between bounds.

    The output is a restraint equation that is meant to be passed to residual.

    eq  --  A node whose value to restrain. This must evaluate to a scalar.
    lb  --  The lower bound on the value of eq. Note that this can be an
            equation.
    ub  --  The upper bound on the value of eq. If ub is None (default), then
            it is set equal to lb.
    sig --  Uncertainty on the bounds (default 1).

    Returns the vector restraint equation:
    resv = max(0, lb - val, val - ub)/sig

    """
    if ub is None: ub = lb
    resv = maximum(lb - eq, maximum(0, eq - ub)) / sig
    resv.name = "restraint"
    return resv