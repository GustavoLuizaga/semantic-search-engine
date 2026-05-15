import xml.etree.ElementTree as ET

class OntologyLoader:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.data_props = {}
        self.obj_props = {}
        self.classes = {}
        self._load()

    def _strip_iri(self, iri: str) -> str:
        if iri and iri.startswith("#"):
            return iri[1:]
        return iri

    def _load(self):
        tree = ET.parse(self.filepath)
        root = tree.getroot()
        
        for elem in root:
            tag = elem.tag.split("}")[-1]
            
            if tag == "ClassAssertion":
                cls_iri = None
                ind_iri = None
                for child in elem:
                    child_tag = child.tag.split("}")[-1]
                    if child_tag == "Class":
                        cls_iri = self._strip_iri(child.get("IRI", child.get("abbreviatedIRI", "")))
                    elif child_tag == "NamedIndividual":
                        ind_iri = self._strip_iri(child.get("IRI", child.get("abbreviatedIRI", "")))
                if cls_iri and ind_iri:
                    self.classes[ind_iri] = cls_iri
                    if ind_iri not in self.data_props:
                        self.data_props[ind_iri] = {}
                    if ind_iri not in self.obj_props:
                        self.obj_props[ind_iri] = []
                        
            elif tag == "DataPropertyAssertion":
                prop_iri = None
                ind_iri = None
                val = None
                for child in elem:
                    child_tag = child.tag.split("}")[-1]
                    if child_tag == "DataProperty":
                        prop_iri = self._strip_iri(child.get("IRI", child.get("abbreviatedIRI", "")))
                    elif child_tag == "NamedIndividual":
                        ind_iri = self._strip_iri(child.get("IRI", child.get("abbreviatedIRI", "")))
                    elif child_tag == "Literal":
                        val = child.text
                if prop_iri and ind_iri and val is not None:
                    if ind_iri not in self.data_props:
                        self.data_props[ind_iri] = {}
                    self.data_props[ind_iri][prop_iri] = val

            elif tag == "ObjectPropertyAssertion":
                prop_iri = None
                inds = []
                for child in elem:
                    child_tag = child.tag.split("}")[-1]
                    if child_tag == "ObjectProperty":
                        prop_iri = self._strip_iri(child.get("IRI", child.get("abbreviatedIRI", "")))
                    elif child_tag == "NamedIndividual":
                        inds.append(self._strip_iri(child.get("IRI", child.get("abbreviatedIRI", ""))))
                if prop_iri and len(inds) == 2:
                    subj_iri, obj_iri = inds
                    if subj_iri not in self.obj_props:
                        self.obj_props[subj_iri] = []
                    self.obj_props[subj_iri].append((prop_iri, obj_iri))
