"""Base classes used in constructing ontologies."""
from itertools import chain

from six import with_metaclass

from ontology_alchemy.proxy import LiteralPropertyProxy, PropertyProxy
from ontology_alchemy.session import Session


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
        cls.label = LiteralPropertyProxy(name="label")
        cls.comment = LiteralPropertyProxy(name="comment")
        cls.seeAlso = PropertyProxy(name="seeAlso")
        cls.isDefinedBy = PropertyProxy(name="isDefinedBy")
        cls.value = PropertyProxy(name="value")

        Session.get_current().register_class(cls)
        return super(RDFS_ClassMeta, cls).__init__(name, bases, dct)


class RDFS_PropertyMeta(RDFS_ClassMeta):
    """
    Metaclass for the `RDFS_Property` class.

    This metaclass governs the creation of all property classes which correspond
    to an RDFS.Property resource.

    """
    def __init__(cls, name, bases, dct):
        # Define proxies for the core RDFS properties as defined in the RDF Schema specification
        cls.domain = PropertyProxy(name="domain")
        cls.range = PropertyProxy(name="range")

        return super(RDFS_PropertyMeta, cls).__init__(name, bases, dct)


class RDFS_Class(with_metaclass(RDFS_ClassMeta)):
    """
    Base class for all dynamically-generated ontology classes corresponding
    to the RDFS.Class resource.

    """

    def __init__(self, **kwargs):
        # Define proxies for the core RDFS properties as defined in the RDF Schema specification
        self.label = LiteralPropertyProxy(name="label")
        self.comment = LiteralPropertyProxy(name="comment")
        self.seeAlso = PropertyProxy(name="seeAlso")
        self.isDefinedBy = PropertyProxy(name="isDefinedBy")
        self.value = PropertyProxy(name="value")

        for property_class in self.__class__.__properties__:
            setattr(self, property_class.__name__, PropertyProxy.for_(property_class))

        for k, v in kwargs.items():
            property_proxy = getattr(self, k)
            property_proxy += v

        Session.get_current().register_instance(self)


class RDFS_Property(with_metaclass(RDFS_PropertyMeta, RDFS_Class)):
    """
    Base class for all dynamically-generated ontology property classes
    corresponding to the RDFS.Property resource.

    """

    def __init__(self, *args, **kwargs):
        super(RDFS_Property, self).__init__(*args, **kwargs)

    def __str__(self):
        return "<RDFS_Property label={}, domain={}, range={}>".format(
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
