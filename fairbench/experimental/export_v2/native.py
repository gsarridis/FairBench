from fairbench.experimental.core_v2 import Value, TargetedNumber, Descriptor, Comparison
from fairbench.experimental.export_v2.formats.ansi import ansi
import json
from fairbench.experimental.export_v2.formats.console import Console


def _generate_details(descriptor: Descriptor):
    roles = descriptor.role.split(" ")
    roles = [role for role in roles if role not in descriptor.details]
    roles = " of a ".join(roles)
    details = descriptor.details
    if not roles:
        details = f"This is {details}."
    else:
        details = f"This {roles} is {details}."
    return details


def tojson(value: Value, indent="  "):
    return json.dumps(value.serialize(), indent=indent)


def _console(env: Console, value: Value, depth=0, max_depth=6, symbol_depth=0):
    title = value.descriptor.name

    def get_ideal():
        if isinstance(value.value, TargetedNumber):
            return value.value.target
        return float(value) + 0.5

    if value.value is not None and (depth<max_depth or symbol_depth!=0):
        depth += 1

    if (not value.depends or depth > max_depth or symbol_depth>max_depth) and value.value is not None:
        val = float(value)
        env.bar(title, val, get_ideal())
        return
    if depth > max_depth:
        env.text(f"{title} [use the alias {value.descriptor.alias} for more info]")
        return
    env.title(title, level=symbol_depth)
    env.first().quote(_generate_details(value.descriptor), (" is ", " in ", " of ", " for ")).p()
    if value.value is not None:
        env.first().result("Value:", float(value), get_ideal())
        if isinstance(value.value, TargetedNumber):
            env.text(f" where ideal is {value.value.target:.3f}")
        env.p()
    elif value.depends:
        env.first().bold("A value is computed in the following cases.").p()
    for dep in value.depends.values():
        _console(env, dep, depth, max_depth=max_depth, symbol_depth=symbol_depth+1)
    if not value.depends and value.value is None:
        env.bold("Nothing has been computed").p()


def static(value: Value, depth=0, env=None):
    # depth=0 gets the minimal details that allow exploration of the next step
    assert isinstance(value, Value), (
        "You did not provide a core.Value. Perhaps you accidentally accessed a property of core.Value instead."
        + "Use the full dict notation (e.g., value['branch'] instead of value.branch to avoid this."
    )
    if env is None:
        env = Console()
    _console(env, value, max_depth=depth)
    return env


def help(value: any, details=True):
    def console_details(descriptor):
        return Console().quote(_generate_details(descriptor.prototype), (" is ", " in ", " of ", " for ")).contents

    if isinstance(value, Comparison) or value==Comparison:
        ansi.print("#" * 5 + " FairBench help " + "#" * 5, ansi.green + ansi.bold)
        ansi.print("Comparison", ansi.bold+ansi.blue)
        print("This is a comparison builder.")
        ansi.print("Usage:", ansi.bold)
        if value==Comparison:
            print("- cmp = Comparison(name)".ljust(27), "Creates a comparison with the given name.")
        print("- cmp.instance(name, value)".ljust(27), "Accumulates a new instance holding the given value.")
        print("- cmp.build()".ljust(27), "Creates a value from accumulated instances and clears cmp.")
        print("- cmp.clear()".ljust(27), "Clears cmp by removing all accumulated instances.")
        print()
        return
    if not isinstance(value, Value):
        if hasattr(value, "descriptor"):
            descriptor = value.descriptor
            if isinstance(descriptor, Descriptor):
                alias = descriptor.name
                ansi.print("#" * 5 + " FairBench help " + "#" * 5, ansi.green + ansi.bold)
                ansi.print(alias, ansi.bold+ansi.blue)
                print(console_details(descriptor))
                ansi.print("Usage:", ansi.bold)
                print(f"- value | {alias}".ljust(27), f"Filters a value so that {alias} is the primary focus.")
                if "measure" in descriptor.role:
                    print(f"- {alias}(**kwargs)".ljust(27), "Computes the measure given appropriate arguments.")
                    print(f"- report(measures=[{alias}, ...], ...)")
                if "reduction" in descriptor.role:
                    print(f"- {alias}(values)".ljust(27), "Computes the reduction from an iterable of numeric values.")
                    print(f"- report(reductions=[{alias}, ...], ...)")
                print()
                return
    assert isinstance(value, Value), (
        "You did not provide a fairbench method or value for help. "
        + "Perhaps you accidentally accessed a property of core.Value instead. "
        + "Use the full dict notation (e.g., value['branch'] instead of value.branch to avoid this."
    )
    ansi.print("#"*5 + " FairBench help " + "#"*5, ansi.green+ansi.bold)
    print("Access the following fields of the selected value to explore results:")
    for descriptor in value.keys():
        descriptor = descriptor.prototype
        alias = descriptor.alias
        if " " in alias:
            alias = f"value['{alias}']"
        else:
            alias = "value."+alias
        if details:
            print("-", ansi.colorize(alias.ljust(25), ansi.blue) + " " + console_details(descriptor))
        else:
            print("-", ansi.colorize(alias.ljust(25), ansi.blue) + " " + descriptor.role)
    print()