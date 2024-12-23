# :pencil: Contributing
FairBench was designed to be easily extensible.
We are primarily looking to integrate new or existing
fairness metrics or reduction strategies, 
but any improvement to the
codebase is welcome. :smile:

For a timely processing of a new pull request,
it is preferred (but not mandatory) to have a discussion
in the repository's issues first. You can also e-mail
the project's current maintainer: *Emmanouil (Manios) Krasanakis*
at *maniospas@hotmail.com* .

## Pull checklist

Follow these steps to add new features:

1. Fork the repository.
2. Clone the fork in your local development environment.
3. Install dependencies.
4. Write tests for new code and push the changes in your fork. 
5. Create a pull request from github's interface.

## Create new performance metrics

Create new metrics under the `fairbench.blocks.metrics` module.
If metrics can be computed independently for fork branches,
e.g., independently for each gender, 
add the `@parallel` decorator.
Add the `@role("metric")` decorator on top of every metric 
(over the parallel decorators) to help FairBench understand
the role of any output forks or explainables.
If your implementation uses other decorators, like the `@unit_bounded`
to assert that all inputs values lie in the range [0,1], put them
under the above two decorators.

```
from faibench import parallel

@role("metric")
@parallel
def metric(...):
    return ...
```

Reuse as many arguments found in other metrics as possible. 
Numeric inputs are automatically converted into 
[eagerpy](https://github.com/jonasrauber/eagerpy) tensors,
which use a functional interface to ensure interoperability.
You can use the `@parallel_primitive` decorator to avoid
this conversion and work with the exact primitives 
provided by those working with your method. Try not to do so
without good reason, as it reduces computational equivalence
between environments. If your metric should behave differently for different 
data branches, add a `branch: str = None` default argument in its
definition to get the branch name.

Prefer returning output values as `Explainable` objects. 
These wrap simple numbers with additional metadata to be viewed for
explanation. Some reductions or expansions look at specific
metadata to be computed (e.g., `cmean` requires a *"samples"* 
numbers that stores the group size, `barea` requres a *"curve"*
of the type `Curve` storing x-axis and y-axis plots of some
curve that the metric summarizes). As a prototype to start from, 
this is how `tpr` constructs its explainable output:

```python
return Explainable(
    value,  # this is a positional argument
    samples=...,
    positives=...,
)
```

:bulb: Explainable objects wrap all operations of their
stored value, and can be used for new arithmetics (the
result will be normal numbers).

Try to avoid invalid arithmetic operations (e.g., division
by zero) with appropriate checks, 
but if there are specific cases for which the 
output cannot be computed (not when inputs are invalid)
you can return `ExplainableError(message)`. This will
be viewed as *"---"* in reports but will still have
an `.explain` field, which will be storing the given message.

## Create new reduction strategies

Reduction strategies follow three steps: transformation,
expansion, and reduction. To see how these components are used, read 
[here](https://fairbench.readthedocs.io/advanced/manipulation) .

Expansion methods can be found
in the `fairbench.blocks.expanders` module
and should transform a list into a (typically of equal size or longer)
new list that stores the outcome of comparing the elements
of the original list, for instance pairwise. Start
by enriching the following expander definition:

```python
def expander(values: Iterable[ep.Tensor]) -> Iterable[ep.Tensor]:
    assert isinstance(values, list)
    return ... # a symmetric transformation of the first list here
```

Reducers take lists of values, such as lists produced by
an expander, and perform an aggregation strategy to summarize
it into one float value. Take care for your computations
to be backpropagateable. Add reducers in the 
`fairbench.blocks.reducers` module and start
by enriching the following definition:

```python
def reducer(values: Iterable[ep.Tensor]) -> ep.Tensor:
    assert isinstance(values, list)
    return ... # float value that aggregates the list's elements
```

Inputs to expanders or reducers could be `Explainable`,
and you can check for this with isinstance.
The outcome of expanders could also be explainable, though
reducer outcome will be automatically assigned explanations
based on base measure values (it will forgo your explanations).

If an invalid condition is encountered in some expander
or reducer raise an explainable error per
`raise ExplainableError(message)`. This is the same error
used to indicate uncomputable base measures, though here
it needs to be an exception. Adopt this functionality
when creating reducers that explicitly account for metadata;
in this case, raise the explainable error exception if
inputs are not explainable or the needed computational
branch is missing from the explanation.
