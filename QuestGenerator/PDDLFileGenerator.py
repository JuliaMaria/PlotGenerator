# TODO 1. Convert domain file from XML to PDDL
#  2. Generate PDDL files for all individuals to pass them to planner
import os
from DomainDatabase.DomainDatabase import DomainDatabase


def predicate_representation(predicate):
    r = f"\t\t({predicate['name']}"
    for i, p in enumerate(predicate['parameters']):
        r += f" ?p{i+1} - {p['type']}"
    r += ")"
    return r


def action_representation(operator):
    a = f"\t(:action {operator['name']}"

    # parameters
    a += "\n\t\t:parameters("
    for param_name, param_type in operator["parameters"].items():
        a += f"?{param_name} - {param_type} "
    a += ")"

    # preconditions
    a += "\n\t\t:precondition( and"
    for (precondition_predicate, negation, params) in operator["preconditions"]:
        a += " ("
        if negation:
            a += "not ("
        a += f"{precondition_predicate}"

        for p in params:
            a += f" ?{p}"

        if negation:
            a += ")"
        a += ")"
    a += "\t)"

    # effects
    a += "\n\t\t:effect( and"
    for (effect_predicate, negation, params) in operator["effects"]:
        a += " ("
        if negation:
            a += "not ("
        a += f"{effect_predicate}"

        for p in params:
            a += f" ?{p}"

        if negation:
            a += ")"
        a += ")"
    a += ")"

    a += "\n\t)"
    return a


def parse_to_pddl(filename: str, world_name: str = None):
    dd = DomainDatabase(filename)

    filename_no_ext = os.path.splitext(filename)[0]

    if not world_name:
        world_name = filename_no_ext.split("/")[-1]

    with open(filename_no_ext+'.txt', 'w') as f:
        f.write(f"(define (domain {world_name})")
        f.write("\n\t(:requirements :strips :typing)")

    # types
    done_types = []
    with open(filename_no_ext+'.txt', 'a') as f:
        f.write("\n\t(:types")
        for o in dd.objects:
            if o not in done_types:
                f.write(f" {o}")
                done_types.append(o)
        f.write(")")

    # predicates
    done_predicates = []
    with open(filename_no_ext+'.txt', 'a') as f:
        f.write("\n\t(:predicates")
        for p in dd.predicates:
            if p["name"] not in done_predicates:
                f.write(f"\n{predicate_representation(p)}")
                done_predicates.append(p["name"])
        f.write("\n\t)")

    # actions
    done_actions = []
    with open(filename_no_ext + '.txt', 'a') as f:
        for a in dd.operators:
            if a["name"] not in done_actions:
                f.write(f"\n{action_representation(a)}")
                done_actions.append(a["name"])

    with open(filename_no_ext + '.txt', 'a') as f:
        f.write("\n)")
