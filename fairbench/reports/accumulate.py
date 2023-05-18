from fairbench.forks.fork import parallel, parallel_primitive, astensor
import eagerpy as ep


"""
This module provides helper methods to concatenate tensors stored within Forks of tensor or Forks of dicts of tensors
and use the final output in one report at the end.
"""


@parallel_primitive
def todict(**kwargs):
    if not kwargs:
        return None
    return kwargs


@parallel_primitive
def concatenate(*data):
    data = [d for d in data if d is not None]
    if len(data) == 1:
        return data[0]
    isdict = isinstance(data[0], dict)
    for d in data:
        assert isinstance(d, dict) == isdict
    if isdict:
        return {k: ep.concatenate([astensor(d[k]) for d in data]) for k in data[0]}
    return ep.concatenate([astensor(d) for d in data])


def extract(**kwargs):
    ret = dict()
    for k, v in kwargs.items():
        try:
            if callable(v):
                v = v()  # TODO: this is a hack to supplement the fact that object members are returns as functions by getattr on Forks
        except TypeError:
            pass
        try:
            v = v[k]
        except AttributeError:
            pass
        ret = ret | todict(**{k: v})
    return ret
