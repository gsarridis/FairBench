import eagerpy as ep
from fairbench.core import Explainable, ExplainableError
from fairbench.core.explanation.error import verify
from typing import List


def abs(value):
    if value < 0:
        return -value
    return value


def _sum(values):
    ret = 0
    for value in values:
        ret = value + ret
    return ret


def identical(values: List[ep.Tensor]) -> ep.Tensor:
    verify(
        isinstance(values, list),
        "Can only reduce lists with fairbench.identical. Maybe you meant to use an eagerpy method?",
    )
    for value in values:
        if (value - values[0]).abs().sum() != 0:
            raise ExplainableError(
                "The same value should reside in all branches for identical reducers."
            )
    return values[0]


def max(values: List[ep.Tensor]) -> ep.Tensor:
    verify(
        isinstance(values, list),
        "fairbench.max can only reduce lists. Maybe you meant to use eagerpy.maximum?",
    )
    ret = float("-inf")
    for value in values:
        if value > ret:
            ret = value
    return ret


def budget(values: List[ep.Tensor]) -> ep.Tensor:
    verify(isinstance(values, list), "fairbench.budget can only reduce lists.")
    from math import log  # TODO: make this compatible with backpropagation

    # "An Intersectional Definition of Fairness"
    return max(values).log()


def std(values: List[ep.Tensor]) -> ep.Tensor:
    verify(isinstance(values, list), "fairbench.std can only reduce lists.")
    n = len(values)
    s = 0
    ss = 0
    for val in values:
        s = val + s
        ss = val * val + ss
    variance = (ss - (s * s) / n) / n
    return variance**0.5


def coefvar(values: List[ep.Tensor]) -> ep.Tensor:
    # coefficient of variation
    # adhered to requirements by Campano, F., & Salvatore, D. (2006). Income Distribution: Includes CD. Oxford University Press.
    verify(isinstance(values, list), "fairbench.std can only reduce lists.")
    n = len(values)
    s = 0
    ss = 0
    for val in values:
        s = val + s
        ss = val * val + ss
    variance = (ss - (s * s) / n) / n
    return variance**0.5 * n / s


def gini(values: List[ep.Tensor]) -> ep.Tensor:
    # coefficient of variation
    verify(isinstance(values, list), "fairbench.std can only reduce lists.")
    n = len(values)

    # Mean of the values
    mean = _sum(values) / n

    # Calculate the Gini numerator
    gini_sum = 0
    for i in range(n):
        for j in range(n):
            gini_sum = abs(values[i] - values[j]) + gini_sum

    # Calculate the Gini coefficient
    gini_coefficient = gini_sum / (2 * n * n * mean)
    return gini_coefficient