import os
import xml.etree.ElementTree as ET
from collections import defaultdict

tension_mapper = {
    "+": 1,
    "-": -1,
    "=": 0
}


class DomainDatabase:
    def __init__(self, domain_filename, world_name=None):
        filename_no_ext = os.path.splitext(domain_filename)[0]

        if world_name:
            self.name = world_name
        else:
            self.name = filename_no_ext.split("/")[-1]

        self.objects = defaultdict(list)  # objects
        self.relations = []  # relations
        self.predicates = []  # predicates
        self.operators = []
        self.event_effects = {}  # event effects

        tree = ET.parse(domain_filename)
        root = tree.getroot()

        for child in root:

            # print(child.tag)

            if child.tag == "objects":
                for object in child:
                    self.objects[object.attrib["type"]].append(object.attrib["name"])

            if child.tag == "relations":
                for relation in child:
                    parameters = []
                    for parameter in relation:
                        parameters.append(parameter.attrib["value"])
                    self.relations.append(self.relation_representation(relation.attrib["name"], parameters))

            if child.tag == "predicates":
                for predicate in child:
                    parameters = []
                    for parameter in predicate:
                        parameters.append(parameter.attrib)
                    self.predicates.append(
                        self.predicate_representation(
                            predicate.attrib.pop('name'),
                            predicate.attrib,
                            parameters
                        )
                    )

            if child.tag == "operators":
                for operator in child:

                    parameters = {}
                    for parameter in operator.find('parameters'):
                        parameters[parameter.attrib['name']] = parameter.attrib['type']

                    preconditions = []
                    for precondition in operator.find('preconditions'):
                        params = [param.attrib['name'] for param in precondition]

                        negation = None
                        try:
                            if precondition.attrib['negation'] == 'true':
                                negation = 'not'
                        except KeyError:
                            pass

                        p = (precondition.attrib['predicate'],
                             negation,
                             params)
                        preconditions.append(p)

                    effects = []
                    for effect in operator.find('effects'):
                        params = [param.attrib['name'] for param in effect]

                        negation = None
                        try:
                            if effect.attrib['negation'] == 'true':
                                negation = 'not'
                        except KeyError:
                            pass

                        e = (effect.attrib['predicate'],
                             negation,
                             params)
                        effects.append(e)

                    self.operators.append(
                        self.operator_representation(
                            operator.attrib['name'],
                            parameters,
                            preconditions,
                            effects
                        )
                    )

            if child.tag == "eventeffects":
                for eventeffect in child:
                    self.event_effects[eventeffect.attrib["name"]] = tension_mapper[eventeffect.attrib["tension"]]

        # print(self.objects)
        # print(self.relations)
        # print(self.predicates)
        # print(self.event_effects)

    def object_representation(self, type, name):
        return {"type": type, "name": name}

    def relation_representation(self, name, values):
        return {"name": name, "values": values}

    def predicate_representation(self, name, attributes, parameters):
        return {
            "name": name,
            "attributes": attributes,
            "parameters": parameters
        }

    def operator_representation(self, name, parameters, preconditions, effects):
        return {
            "name": name,
            "parameters": parameters,
            "preconditions": preconditions,
            "effects": effects
        }
