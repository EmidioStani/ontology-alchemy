"""Base classes used in constructing ontologies."""
from itertools import chain
from random import choice
from string import ascii_lowercase, ascii_uppercase, digits
import re
import configparser
import time
import codecs

from rdflib.namespace import RDF, RDFS, SKOS
from six import with_metaclass

from ontology_alchemy.proxy import LiteralPropertyProxy, PropertyProxy
from ontology_alchemy.session import Session

def strip_from_uri(uri):
    splituri = re.split("\|/|#",uri)
    return splituri[-1]

def generate_uri(base_uri, random_length=8):
    random_id = "".join(
        choice(ascii_uppercase + ascii_lowercase + digits)
        for _ in range(random_length)
    )
    return "{}_{}".format(base_uri, random_id)

class URISpecification:

    def __init__(self, def_base_uri, dict1):
        self.base_uri = def_base_uri
        self.dict1 = dict1

    def getURI(self,fullType):
        self.component_type = strip_from_uri(fullType)
        self.encodedstring = codecs.encode(self.dict1["label"], "rot-13")#.encode('base64','strict')
        self.unicity = int(time.time() * 1000)
        return self.base_uri + self.component_type + "/" + self.encodedstring + "-" + str(self.unicity)



class RDFS_ClassMeta(type):
    """
    Metaclass for the `RDFS_Class` class.

    This metaclass governs the creation of all classes which correspond
    to an RDFS.Class resource.

    """
    def __new__(meta_cls, name, bases, dct):
        dct.setdefault("__properties__", [])
        dct.setdefault("__uri__", None)

        return super(RDFS_ClassMeta, meta_cls).__new__(meta_cls, name, bases, dct)

    def __init__(cls, name, bases, dct):
        # Define proxies for the core RDFS properties as defined in the RDF Schema specification
        cls.label = LiteralPropertyProxy(name="label", uri=RDFS.label)
        cls.comment = LiteralPropertyProxy(name="comment", uri=RDFS.comment)
        cls.seeAlso = PropertyProxy(name="seeAlso", uri=RDFS.seeAlso)
        cls.isDefinedBy = PropertyProxy(name="isDefinedBy", uri=RDFS.isDefinedBy)
        cls.value = PropertyProxy(name="value", uri=RDF.value)

        # Define proxies for other common properties
        cls.prefLabel = LiteralPropertyProxy(name="prefLabel", uri=SKOS.prefLabel)

        Session.get_current().register_class(cls)
        return super(RDFS_ClassMeta, cls).__init__(name, bases, dct)


class RDF_PropertyMeta(RDFS_ClassMeta):
    """
    Metaclass for the `RDF_Property` class.

    This metaclass governs the creation of all property classes which correspond
    to an RDFS.Property resource.

    """
    def __init__(cls, name, bases, dct):
        # Define proxies for the core RDFS properties as defined in the RDF Schema specification
        cls.domain = PropertyProxy(name="domain", uri=RDFS.domain)
        cls.range = PropertyProxy(name="range", uri=RDFS.range)

        return super(RDF_PropertyMeta, cls).__init__(name, bases, dct)


class RDFS_Class(with_metaclass(RDFS_ClassMeta)):
    """
    Base class for all dynamically-generated ontology classes corresponding
    to the RDFS.Class resource.

    """

    def __init__(self, uri=None, **kwargs):
        # Define proxies for the core RDFS properties as defined in the RDF Schema specification
        self.label = LiteralPropertyProxy(name="label", uri=RDFS.label)
        self.prefLabel = LiteralPropertyProxy(name="prefLabel", uri=SKOS.prefLabel)
        self.comment = LiteralPropertyProxy(name="comment", uri=RDFS.comment)
        self.seeAlso = PropertyProxy(name="seeAlso", uri=RDFS.seeAlso)
        self.isDefinedBy = PropertyProxy(name="isDefinedBy", uri=RDFS.isDefinedBy)
        self.value = PropertyProxy(name="value", uri=RDF.value)
        self.uriHandle = uri# or generate_uri(self.__class__.__uri__)
        self.type = PropertyProxy(name="type", uri=RDF.type)

        for property_class in self.__class__.__properties__:
            setattr(self, property_class.__name__, PropertyProxy.for_(property_class))

        # Generate the URI
        if uri != None:
            self.uri = self.uriHandle.getURI(self.__class__.__uri__)

        for k, v in kwargs.items():
            if k == "imposeURI":
                self.uri = v # overwrite computed URI with imposed one
            else:
                property_proxy = getattr(self, k)
                property_proxy += v


        self.addType(self.__class__.__uri__)

        Session.get_current().register_instance(self)

    def addType(self,uri):
        # Set the type
        property_proxy = getattr(self, "type")
        property_proxy += uri

    def iter_rdf_statements(self):
        """
        Returns an iterable over (subject, predicate, object) triples
        representing all of the relations and assigments represented in the class instance.

        """
        for value in self.__dict__.values():
            if isinstance(value, PropertyProxy):
                property_name = value.name
                property_uri = value.uri
                for property_value in getattr(self, property_name):
                    yield (self.uri, property_uri, property_value)

    def getInstanceUri(self):
        return self.uri


class RDF_Property(with_metaclass(RDF_PropertyMeta, RDFS_Class)):
    """
    Base class for all dynamically-generated ontology property classes
    corresponding to the RDFS.Property resource.

    """

    def __init__(self, *args, **kwargs):
        super(RDF_Property, self).__init__(*args, **kwargs)

    def __str__(self):
        return "<RDF_Property label={}, domain={}, range={}>".format(
            self.label,
            self.domain,
            self.range,
        )

    @classmethod
    def inferred_domain(cls):
        """
        Calculate the full domain for this property class based on traversing up the full
        property inheritance hierarchy.

        """
        return cls.domain.values + list(
            chain.from_iterable(
                base_class.inferred_domain()
                for base_class in cls.__bases__
                if getattr(base_class, 'domain', None)
            )
        )

    @classmethod
    def inferred_range(cls):
        """
        Calculate the full range for this property class based on traversing up the full
        property inheritance hierarchy.

        """
        return cls.range.values + list(
            chain.from_iterable(
                base_class.inferred_range()
                for base_class in cls.__bases__
                if getattr(base_class, 'range', None)
            )
        )
