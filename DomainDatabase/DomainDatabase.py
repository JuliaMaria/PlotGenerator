import xml.etree.ElementTree as ET
from collections import defaultdict

# TODO Load operators and event effects


class DomainDatabase:
    def __init__(self, domain_filename):
        self.objects = defaultdict(list)  # objects
        self.relations = []  # relations
        self.predicates = []  # predicates

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

        # print(self.objects)
        # print(self.relations)
        # print(self.predicates)

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

#
# dd = DomainDatabase("PlotGenerator/Domain/World.xml")
