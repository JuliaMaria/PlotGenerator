import xml.etree.ElementTree as ET


def object_to_string(type, name):
    return f"{type}({name})"


class DomainDatabase:
    def __init__(self, domain_filename):
        self.objects = []  # objects
        self.relations = []  # relations
        self.predicates = []  # predicates
        self.operators = []  # operators
        self.effects = []  # eventeffects

        tree = ET.parse(domain_filename)
        root = tree.getroot()

        for child in root:
            print(child.tag)

            if child.tag == "objects":
                for object in child:
                    self.objects.append(object_to_string(object.attrib["type"], object.attrib["name"]))

        print(self.objects)


dd = DomainDatabase("../Domain/World.xml")
