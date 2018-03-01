"""
Common schema definition types that should be mapped to corresponding Python objects.

Some of the primary mappings of interest include:

* the rdfs:Class type which should be mapped to Python class
* the rdfs:subClassOf property type which should be mapped to an inheritance relation

"""
from string import ascii_lowercase

from rdflib import Literal
from rdflib.namespace import RDF, RDFS, OWL, XSD
from six import string_types
from six.moves.urllib.parse import urlparse
import re

from ontology_alchemy.constants import COMMON_PROPERTY_URIS


def in_namespace(uri, base_uri):
    """
    Check if given URI is in the "namespace" of the given base URI

    """
    if any((
        base_uri.endswith("#"),
        base_uri.endswith("/")
    )):
        # We chop off last character of base uri as that typically can include a
        # backslash (/) or a fragment (#) character.
        base_uri = base_uri[:-1]
    return uri.startswith(base_uri)


def is_a_class(uri):
    return uri in (
        RDFS.Class,
        OWL.Class,
    )


def is_a_property(uri):
    return uri in COMMON_PROPERTY_URIS


def is_a_property_subtype(uri, type_graph=None):
    return any((
        type_graph and is_a_property(type_graph.get(uri)),
        looks_like_a_property_uri(uri),
    ))


def is_a_list(uri):
    return uri in (
        RDF.List,
    )


def is_a_literal(uri):
    return (uri in (RDFS.Literal,) or
            uri.startswith(XSD))


def is_literal_value(value):
    return (
        isinstance(value, Literal) or
        isinstance(value, string_types)
    )


def is_comment_predicate(predicate):
    return predicate in (
        RDFS.comment,
    )


def is_domain_predicate(predicate):
    return predicate in (
        RDFS.domain,
    )


def is_label_predicate(predicate):
    return predicate in (
        RDFS.label,
    )


def is_range_predicate(predicate):
    return predicate in (
        RDFS.range,
    )


def is_type_predicate(predicate):
    return predicate in (
        RDF.type,
    )


def is_sub_class_predicate(predicate):
    return predicate in (
        RDFS.subClassOf,
    )


def is_sub_property_predicate(predicate):
    return predicate in (
        RDFS.subPropertyOf,
    )


def looks_like_a_property_uri(uri):
    """
    Heuristic for checking if a given URI "looks like" a Property type or an Class type.
    By widely followed convention, properties use lowercase first letter and classes use a capital
    first letter for the type.

    """
    # name = urlparse(uri).path
    splituri = re.split("#",uri)
    splituri = re.split("/",splituri[-1])
    name = splituri[-1]
    # print("-->", name)
    return name[0] in ascii_lowercase
