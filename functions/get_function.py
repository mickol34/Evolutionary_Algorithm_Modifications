from inspect import getmembers, isfunction

import typing

try:
    import cec2017.functions
    import cec2017.basic
except Exception as error:
    raise Exception(f"Błąd importowania modułu: [{error}]")

import functions.mutation_functions
import functions.population_functions
import functions.selection_functions
import functions.objective_functions


def mutation(function_name: str = "") -> typing.Callable or None:
    return __get_member(member_name=function_name,
                        members=getmembers(functions.mutation_functions, predicate=isfunction))


def population(function_name: str = "") -> typing.Callable or None:
    return __get_member(member_name=function_name,
                        members=getmembers(functions.population_functions, predicate=isfunction))


def selection(function_name: str = "") -> typing.Callable or None:
    return __get_member(member_name=function_name,
                        members=getmembers(functions.selection_functions, predicate=isfunction))


def q(function_name: str = "f4") -> typing.Callable or None:
    for function in cec2017.functions.all_functions:
        if function.__name__ == function_name.strip():
            return function

    return __get_member(member_name=function_name,
                        members=getmembers(functions.objective_functions, predicate=isfunction))



def __get_member(member_name: str, members: list[tuple]) -> typing.Callable or None:
    for name, member in members:
        if name == member_name:
            return member
    return None
