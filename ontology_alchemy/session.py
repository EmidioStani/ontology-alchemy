"""The session is a global context for all objects created from an Ontology."""
from itertools import chain

from contextlib2 import contextmanager


class Session(object):
    """
    The session object encapsulates a global context for objects created
    with respect to an ontology.

    By default a single session object is created and can be retrieved
    with Session.get_current().
    Additionally, sessions can be pushed unto a stack for limiting scope
    using the `session_context` method, when used as a context manager or decorator:

    >>> with session_context() as session:
    ...     # Create ontology, instantiate classes
    ...     ontology = Ontology.load("my-ontology.ttl")
    ...     instance = ontology.Corporation(label="Acme Inc.")
    ...     assert instance in Session.get_current().instances
    ... assert instance not in Session.get_current().instances

    """
    stack = []

    def __init__(self, classes=None, instances=None):
        self.classes = classes or []
        self.instances = instances or []

    @classmethod
    def get_current(cls):
        return cls.stack[-1]

    def clear(self):
        """
        Clear the session instance of all registered objects.

        """
        self.classes = []
        self.instances = []

    def register_class(self, klass):
        """
        Register a new Python class corresponding to an Ontology class.

        :param klass - the Python class to register

        """
        self.classes.append(klass)

    def register_instance(self, instance):
        """
        Register a new instance of a Python class corresponding to an Ontology class.

        :param instance - the Python class instance to register

        """
        self.instances.append(instance)

    def rdf_statements(self):
        """
        Return iterable over (subject, predicate, object) statements
        representing all instances created since session started.

        """
        return chain.from_iterable(
            instance.iter_rdf_statements()
            for instance in self.instances
        )


@contextmanager
def session_context():
    session = Session()
    Session.stack.append(session)
    yield session
    Session.stack.pop()


# Populate default session
Session.stack.append(Session())
