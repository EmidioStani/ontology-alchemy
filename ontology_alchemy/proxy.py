"""Proxy objects."""
from rdflib import Literal
from six import string_types, text_type

from ontology_alchemy.constants import DEFAULT_LANGUAGE_TAG, LITERAL_PRIMITIVE_TYPES


class PropertyProxy(object):
    """
    A proxy class for accessing RDFS.Property instances as Python class instance attributes.
    It supports evaluating whether a given value assignment is valid based on the RDF definitions
    of domain and range.

    """

    def __init__(self, name=None, uri=None, values=None, domain=None, range=None):
        self.name = name
        self.uri = uri
        self.values = values or []
        self.domain = domain or []
        self.range = range or []

    def __str__(self):
        return "<PropertyProxy name={}, uri={}, domain={}, range={}, values={}>".format(
            self.name,
            self.uri,
            self.domain,
            self.range,
            self.values,
        )

    def __call__(self, value=None):
        return value in self.values

    def __iadd__(self, value):
        if isinstance(value,str) and value.startswith("http://"):
            pass # points to URI, assume URI is correct
        else:
            if not self.is_valid(value):
                raise ValueError("{}({}): Invalid assigment. property value must be one of range={}, but got: {}"
                                 .format(self.__class__.__name__, self.name, self.range, value))
        self.add_instance(value)
        return self

    def __iter__(self):
        return iter(self.values)

    @classmethod
    def for_(cls, property_cls):
        if property_cls.range.values == [Literal]:
            # For exclusively literal-valued properties
            cls = LiteralPropertyProxy

        return cls(
            name=property_cls.__name__,
            uri=property_cls.__uri__,
            domain=property_cls.domain,
            range=property_cls.inferred_range(),
        )

    def add_instance(self, value):
        self.values.append(value)

    def is_valid(self, value):
        if not self.range or any(
            isinstance(value, range_resource)
            for range_resource in self.range
        ):
            return True


class LiteralPropertyProxy(PropertyProxy):
    def __call__(self, lang=None):
        if lang:
            return [
                text_type(literal)
                for literal in self.values
                if literal.language == lang
            ] or None
        else:
            return self.values

    def add_instance(self, value):
        if not isinstance(value, Literal):
            if isinstance(value, string_types):
                # if is a textual string, enforce assigning a language tag
                value = Literal(value, lang=DEFAULT_LANGUAGE_TAG)

        self.values.append(value)

    def is_valid(self, value):
        if isinstance(value, LITERAL_PRIMITIVE_TYPES):
            return True
