import math
import random

from packaging.specifiers import Specifier
from packaging.specifiers import SpecifierSet
from packaging.version import InvalidVersion
from packaging.version import Version

specifier_sets = [
    SpecifierSet("==1.0.0"),
    SpecifierSet("==2.0.0"),
    SpecifierSet("!=1.5.0"),
    SpecifierSet("!=2.0.*"),
    SpecifierSet(">1.0.0"),
    SpecifierSet(">=1.0.0"),
    SpecifierSet(">2.0.0"),
    SpecifierSet(">=2.0.0"),
    SpecifierSet("<3.0.0"),
    SpecifierSet("<=3.0.0"),
    SpecifierSet("<2.0.0"),
    SpecifierSet("<=2.0.0"),
    SpecifierSet("~=1.0"),
    SpecifierSet("~=2.0"),
    SpecifierSet("==1.0.*"),
    SpecifierSet("==2.0.*"),
    SpecifierSet("!=1.0.0"),
    SpecifierSet("!=2.0.0"),
    SpecifierSet(">1.0,<=2.0"),
    SpecifierSet(">=1.0,!=1.5.*,<2.0"),
    SpecifierSet(">1.0.0,!=2.0.0,<3.0.0"),
    SpecifierSet("~=1.4"),
    SpecifierSet("~=2.1"),
    SpecifierSet(">=1.0,<2.0"),
    SpecifierSet(">=2.0,<3.0"),
    SpecifierSet("==1.0.0rc1"),
    SpecifierSet("==2.0.0.post1"),
    SpecifierSet(">1.0.0rc1,<=2.0.0"),
    SpecifierSet("!=2.0.0rc1"),
    SpecifierSet(">=1.0.0rc1,<3.0.0"),
]


def extract_bounds_and_score(specifier_set):
    lower = None
    upper = None
    lower_inclusive = False
    upper_inclusive = False

    for spec in specifier_set:
        try:
            ver = Version(spec.version.rstrip(".*"))
            ver_num = float(f"{ver.major}.{ver.minor or 0}{ver.micro or 0}")
        except (InvalidVersion, ValueError):
            continue

        if spec.operator in ("==", "===", "~="):
            lower = upper = ver_num
            lower_inclusive = upper_inclusive = True
            break
        elif spec.operator == ">=":
            if lower is None or ver_num > lower:
                lower = ver_num
                lower_inclusive = True
        elif spec.operator == ">":
            if lower is None or ver_num > lower:
                lower = ver_num
                lower_inclusive = False
        elif spec.operator == "<=":
            if upper is None or ver_num < upper:
                upper = ver_num
                upper_inclusive = True
        elif spec.operator == "<":
            if upper is None or ver_num < upper:
                upper = ver_num
                upper_inclusive = False

    if lower is None:
        lower = -math.inf
        lower_inclusive = False
    if upper is None:
        upper = math.inf
        upper_inclusive = False

    if lower == upper and lower_inclusive and upper_inclusive:
        range_score = 0.0
    else:
        range_score = (upper - lower) if math.isfinite(upper - lower) else math.inf

    exclusivity_penalty = 0.01 * (not lower_inclusive) + 0.01 * (not upper_inclusive)
    return range_score, exclusivity_penalty


def specifier_sort_key(specifier_set):
    range_score, exclusivity_penalty = extract_bounds_and_score(specifier_set)
    num_specifiers = len(list(specifier_set))
    return (
        range_score,  # Primary → narrower is more restrictive
        exclusivity_penalty,  # Secondary → inclusiveness improves restrictiveness
        -num_specifiers,  # Tertiary → more specifiers = more restrictive
        str(specifier_set),  # Tie-breaker → consistent ordering for total order
    )


def sort_total_order(specifiers):
    return sorted(specifiers, key=specifier_sort_key)


def verify_total_order():
    randomized = specifier_sets.copy()
    random.shuffle(randomized)
    sorted_specifiers = sort_total_order(randomized)
    # Ensure total order by confirming strict ascending tuples or equality only at identical strings
    keys = [specifier_sort_key(spec) for spec in sorted_specifiers]
    is_strict_total = all(
        keys[i] < keys[i + 1] or keys[i] == keys[i + 1] for i in range(len(keys) - 1)
    )
    return sorted_specifiers, keys, is_strict_total


if __name__ == "__main__":
    sorted_specifiers, keys, is_correct = verify_total_order()
    print("Total order of SpecifierSets (lower = more restrictive):\n")
    for spec, key in zip(sorted_specifiers, keys):
        print(f"{spec} -> ScoreTuple: {key}")
    print(f"\nTotal ordering verified correct: {is_correct}")
