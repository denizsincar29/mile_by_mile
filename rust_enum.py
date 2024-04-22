# a simple implementation of rust enum in python
# a short doc:
# initialize the enum with the @enum decorator
# each field of the enum should be an instance of the Case class
# the parentheses should be used even if the Case class does not have any attributes
# not val=Case, but val=Case()
# when matching, use parens even if the Case class does not have any attributes
# in rust parens are not used, but in python they are required
# when initializing an enum field, use parens even if the Case class does not have any attributes
# parens are everywhere, remember that!
# good luck, my dear python-rustacean xD!


from dataclasses import make_dataclass
from typing import Any


def enum(cls):
    for field_name in dir(cls):
        if not isinstance((value := getattr(cls, field_name)), Case): 
            continue
        
        setattr(cls, field_name, make_dataclass(
            field_name, list(value.dict.items()), bases=(cls, )
        ))
    return cls


class Case:
    def __init__(self, **attributes):
        self.dict = attributes

    # to disable warnings
    def __call__(self, *args, **kwargs):
        pass


@enum
class Result:
    Ok=Case(val=Any)
    Err=Case(val=Exception)


@enum
class Option:
    Something=Case(val=Any)
    Nothing=Case()

if __name__ == "__main__":
    nothing=Option.Nothing()
    match nothing:
        case Option.Nothing():
            print("Nothing")
        case Option.Something(val):
            print(val)