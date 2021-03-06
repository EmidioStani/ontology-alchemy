# ontology-alchemy

ontology-alchemy makes using [RDF](https://en.wikipedia.org/wiki/Resource_Description_Framework) [ontology](https://en.wikipedia.org/wiki/Ontology_(information_science)) definitions to create Python class hierarchies easy.

[![CircleCI](https://circleci.com/gh/globality-corp/ontology-alchemy/tree/develop.svg?style=svg)](https://circleci.com/gh/globality-corp/ontology-alchemy/tree/develop)

## Overview

This project aims to make it easy to work programmatically with RDF Ontologies. RDF Ontologies are prelevant in the world of [Semantic Web](https://en.wikipedia.org/wiki/Semantic_Web). Notable projects using these include [schema.org](http://schema.org), which includes a general ontology that can be used by websites to describe their contents, and [DBPedia](http://wiki.dbpedia.org) which maintains a curated, multi-lingual structured knowledge graph based on Wikipedia.

While the RDF Schema ([RDFS](https://www.w3.org/TR/rdf-schema/)) data model is a similar paradigm in many respects to that of Object Oriented Programming (OOP), mapping from RDF ontologies to programmatic objects is not straight forward - in RDF, the emphasis is on the predicates (which can be thought of as graph edges, or object properties), and a given object can be tied to arbitrary properties; moreover, multiple assigments of a given predicate type can be tied to an object - e.g we can assert multiple rdfs:label associations for any given subject (instance). Further, validation of property assigment (e.g rdf:Property domain and range) is not strictly enforced in the original RDF/RDFS specifications and is left as an application-specific decision.
To bridge some of these differences, this framework sets forth a few opinionated conventions for translating RDF/RDFS definitions to Pythonic OOP-style code.

Some of the main tasks made possible with this library include:

* Loading an existing, serialized RDF Ontology (e.g from a Turtle/N3 formatted file) into Python code, allowing introspection of the ontology. The parsing heavy-lifting is done via [rdflib](http://rdflib.readthedocs.io/en/stable/), and the parsed RDF Graph is then further processed to dynamically build a Python class hierarchy
* Creating Pythonic class instances using the types defined in the ontology, including properties and relations, as well as native data types
* Validation on property value types based on ontology definitions
* Easy interfacing to persistence layer by a Session abstraction which exposes all instances created in an easy-to-use way

## Usage

The package is compatible with Python 2.7 or 3.x. To install from PyPI, simple as:

    pip install ontology-alchemy

Assuming an existing RDF ontology definition serialized in [Turtle](https://en.wikipedia.org/wiki/Turtle_(syntax)), you could then do:

```python
from ontology_alchemy import Ontology, Session

# Load ontology definition, create all Python classes
ontology = Ontology.load("my-ontology.ttl")

# Can then define particular instances.
china = ontology.Country(label="China", comment="People's Republic of China")
united_states = ontology.Country(label="United States", comment="United States of America")

print(united_states.label(lang="en"))
print(united_states.comment(lang="en"))

us_dollar = ontology.Currency(label="U.S Dollar")
american_english = ontology.Language(label="American English")
mandarin = ontology.Language(label="Mandarin")
cantonese = ontology.Language(label="Cantonese")
```

**Property** assigment and access is fairly intuitive as well:

```python
# Property assigments are done using += to reflect the fact that multiple "edges"
# of a particular type (predicate) can exist for an object
china.officialLanguage += mandarin
china.officialLanguage += cantonese

# Can assert if a particular property assigment already exists
print(china.officialLanguage(mandarin))  # Will evaluate to true

# The following assignment will raise an exception: officialLanguage
# is a property (rdf:Property) which has Language as its range
united_states.officialLanguage += us_dollar
```

**Inheritance** works as expected. All sub-classes of a given class (defined via the rdfs:subClassOf predicate)
will inherit its properties. In addition, rdfs:subPropertyOf relations are properly supported:


```python
# Actor is a rdfs:subClassOf of Person
brad = ontology.Actor(label="Brad Pitt")
angelina = ontology.Actor(label="Angelina Jolie")

# Person defines rdf:Property 'marriedTo' so it can be used by Actor as well
brad.marriedTo += angelina

# Assuming 'marriedTo' as defined with rdf:subPropertyOf relation to a hypothetical
# 'livesWith' rdfs:Property defines on Person the following will evaluate to true
brad.livesWith(angelina)

```

Interfacing with a persistent backend is easy by leveraging the `Session` interface
to enumerate all created classes and instances. These can then be fed into any storage backend
by writing appropriate glue layer:

```python
from ontology_alchemy.session import Session

# Get all programmatic class instances created since process started
session = Session.get_current()
print(session.classes)

# Stream RDF statements capturing all class instances, properties and relations created
for (subject, predicate, object) in session.rdf_statements():
    print(subject, predicate, object)
```

Sessions can also be scoped using the provided context manager and decorator interfaces.

```python
from ontology_alchemy.session import Session, session_context

with session_context() as session:
    ontology = Ontology.load("my-ontology.ttl")
    print(session.classes)  # Will print all Python classes corresponding to ontology classes

session = Session.get_current()
print(session.classes)  # Will be empty - session_context above defined a local session scope
```

See the examples/ folder for a full example.

## Developing

To work on the package locally, create a [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/), and then install package using:

    pip install -e .

To run the provided suite of unit-tests invoke using `nose`:

    python setup.py nosetests

## Similar Projects

* [rdflib](http://rdflib.readthedocs.io/en/stable/) - RDFlib is the de facto standard library for working with RDF and its various serialization formats in Python. It has extensive support for most of the used serialization formats and schema namespaces (such as OWL, RDFS and FOAF), as well as a number of triplestore-style graph iteration APIs and persistent store backend implementations. It does not however aim to cover the interaction between ontology definitions and programmatic instantiation of ontology-defined types. Most of its stores have also fallen out of date and so it does not offer out of the box a viable solution for large-scale persistence of knowledge graph data.
* [Owlready](http://pythonhosted.org/Owlready/index.html) - Exposes a simple interface to load OWL ontologies and create instances as Python classes. Also includes a reasoner engine (HermiT). Main limitation is that it only works with OWL and only supports OWL XML serialization format.
