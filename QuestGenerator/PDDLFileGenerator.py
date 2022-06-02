# TODO 1. Convert domain file from XML to PDDL
#  2. Generate PDDL files for all individuals to pass them to planner
import os
from DomainDatabase.DomainDatabase import DomainDatabase


def predicate_representation(predicate):
    r = f"\t({predicate['name']}"
    for i, p in enumerate(predicate['parameters']):
        r += f" ?p{i+1} - {p['type']}"
    r += ")"
    return r


def relation_representation(relation):
    r = f"\t({relation['name']}"
    for i, p in enumerate(relation['values']):
        r += f" ?p{i+1}"
    r += ")"
    return r


def action_representation(operator):
    a = f"\t(:action {operator['name']}"

    # parameters
    a += "\n\t:parameters ("
    for param_name, param_type in operator["parameters"].items():
        a += f"?{param_name} - {param_type} "
    a += ")"

    # preconditions
    a += "\n\t:precondition ( and"
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
    a += "\n\t:effect ( and"
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


def parse_to_pddl(filename: str):
    dd = DomainDatabase(filename)

    filename_no_ext = os.path.splitext(filename)[0]
    world_name = dd.name

    with open(filename_no_ext+'.txt', 'w') as f:
        f.write(f"(define (domain {world_name})")
        f.write("\n(:requirements :typing)")

    # types
    done_types = []
    with open(filename_no_ext+'.txt', 'a') as f:
        f.write("\n(:types")
        for o in dd.objects:
            if o not in done_types:
                f.write(f" {o}")
                done_types.append(o)
        f.write(")")

    # predicates and relations
    done_predicates = []
    with open(filename_no_ext+'.txt', 'a') as f:
        f.write("\n(:predicates")
        for p in dd.predicates:
            if p["name"] not in done_predicates:
                f.write(f"\n{predicate_representation(p)}")
                done_predicates.append(p["name"])

        for r in dd.relations:
            if r["name"] not in done_predicates:
                f.write(f"\n{relation_representation(r)}")
                done_predicates.append(r["name"])
        f.write("\n)")

    # actions
    done_actions = []
    with open(filename_no_ext + '.txt', 'a') as f:
        for a in dd.operators:
            if a["name"] not in done_actions:
                f.write(f"\n{action_representation(a)}")
                done_actions.append(a["name"])

    with open(filename_no_ext + '.txt', 'a') as f:
        f.write("\n)")
