# TODO 1. Convert domain file from XML to PDDL
#  2. Generate PDDL files for all individuals to pass them to planner
import os
from DomainDatabase.DomainDatabase import DomainDatabase


def predicate_representation(predicate):
    r = f"({predicate['name']}"
    for i, p in enumerate(predicate['parameters']):
        r += f" ?p{i+1} - {p['type']}"
    r += ")"
    return r


def parse_to_pddl(filename: str, world_name: str = None):
    dd = DomainDatabase(filename)

    filename_no_ext = os.path.splitext(filename)[0]

    if not world_name:
        world_name = filename_no_ext.split("/")[-1]

    with open(filename_no_ext+'.txt', 'w') as f:
        f.write(f"(define (domain {world_name})")
        f.write("\n(:requirements :strips :typing)")

    # types
    done_types = []
    with open(filename_no_ext+'.txt', 'a') as f:
        f.write("\n(:types")
        for o in dd.objects:
            if o not in done_types:
                f.write(f" {o}")
                done_types.append(o)
        f.write(")")

    # predicates
    done_predicates = []
    with open(filename_no_ext+'.txt', 'a') as f:
        f.write("\n(:predicates")
        for p in dd.predicates:
            if p["name"] not in done_predicates:
                f.write(f"\n{predicate_representation(p)}")
                done_predicates.append(p["name"])
        f.write("\n)")

    with open(filename_no_ext + '.txt', 'a') as f:
        f.write("\n)")
