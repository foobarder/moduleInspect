from importlib import import_module
from pkgutil import walk_packages
import operator
import inspect
import pydoc
import sys
import re
from mergetools import join_members


class Module:
    """class Module(module_name) 
    Class Module gets all the submodules, classes, class_methods and functions of 
    the module taken as an argument by its instance. Every instance of the class has:
    ATTRIBUTES: Module.module_name, self.module, self.submodules, self.functions, self.classes, self.class_methods
    METHODS: self.get_module_version(self), self.get_submodules(self), self.get_functions(self), self.get_classes(self),
    self.get_class_methods(), self.isimported(self, name), self.get_mlattr(self, full_name), self.get_submodule(self, attr)."""

    def __init__(self, module_name):
        self.module_name = module_name
        self.module = import_module(self.module_name)

        self.submodules = self.get_submodules()
        self.functions = self.get_functions()
        self.classes = self.get_classes()
        self.class_methods = self.get_class_methods()

    def get_module_version(self):
        """get_module_version(self) Module method
        return the version of the module taken as an instance argument."""
        return self.module.__version__

    def get_submodules(self):
        """get_submodules(self) Module method
        return a list of submodules of the module taken as an instance argument."""
        submodules = {}
        for loader, name, is_pkg in walk_packages(self.module.__path__, self.module.__name__ + '.'):
            if self.is_imported(name):
                submodules[name] = self.get_submodule(self.get_mlattr(name))
        return submodules

    def get_functions(self):
        """get_functions(self) Module method
        return a list of functions of the module taken as an instance argument."""
        functions = {}
        for submodule_name, submodule in self.submodules.items():
            for function_name, function in inspect.getmembers(submodule, lambda f: inspect.isfunction(f) or inspect.isbuiltin(f)):
                functions[join_members(submodule_name, function_name)] = function
        return functions

    def get_classes(self):
        """get_classes(self) Module method
        return a list of classes of the module taken as an instance argument."""
        classes = {}
        for submodule_name, submodule in self.submodules.items():
            for class_name, class_ in inspect.getmembers(submodule, lambda c: inspect.isclass(c)):
                classes[join_members(submodule_name, class_name)] = class_
        return classes

    def get_class_methods(self):
        """get_class_methods(self) Module method
        return a list of class methods of the module taken as an instance argument."""
        methods = {}
        for class_name, class_ in self.classes.items():
            for method_name, method in inspect.getmembers(class_, lambda m: inspect.ismethod(m) or inspect.isbuiltin(m)):
                methods[join_members(class_name, method_name)] = method
        return methods

    def is_imported(self, submodule_name):
        """is_imported(self, submodule_name) Module method
        retrun True if submodule was imported and False otherwise."""
        return submodule_name in sys.modules

    def get_mlattr(self, full_name):
        """get_mlattr(self, full_name) Module method
        return a multi-level attribute of an object."""
        return full_name.split('.', 1)[1]

    def get_submodule(self, attr):
        """get_submodule(self, attr) Module method
        return submodule object of the module by its attribute."""
        return operator.attrgetter(attr)(self.module)


def get_name(obj):
    """get_name(obj) return object name."""
    return obj.__name__


def get_doc_string(obj):
    """get_doc_string(obj) return object doc string"""
    return re.sub('\x08.', '', pydoc.render_doc(obj)) or obj.__doc__


def get_prefix(name):
    """get_prefix(name) return object prefix."""
    return name.split('.', 1)[1].rsplit('.', 1)[0]


def strip_text(string):
    """strip_text(string) strip \b and \n literals off the string."""
    return re.sub('\x08.', '', string.replace('\n', ''))


def get_argnames(obj):
    """get_argnames(obj) return a tuple of the object argument names."""
    if inspect.isbuiltin(obj):
        function_name = get_name(obj)
        function_doc = obj.__doc__ or strip_text(pydoc.render_doc(obj))
        pattern = function_name + '\(.+?\)'
        match = re.search(pattern, function_doc)
        if match:
            args = match.group().strip(function_name).translate(None, '()').split(',')
            return tuple(re.search('\w+', arg).group() if re.search('\w+', arg) else None for arg in args)
        else:
            return (None,)
    else:
        return tuple(inspect.getargspec(obj).args)


def get_argtypes(obj, defaults):
    """get_argtypes(obj, defaults) return a tuple of the object argument types."""
    return ('arg_type',) * len(defaults)


def get_argdefvalues(obj, args):
    """get_argdefvalues(obj, args) return a tuple of the object argument default values."""
    if inspect.isbuiltin(obj):
        return ('builtin arg value',) * len(args)
    else:
        argspec = inspect.getargspec(obj)
        arguments = argspec.args
        defaults = argspec.defaults
        if defaults:
            signature = dict(zip(arguments[-len(defaults):], defaults))
            return tuple(signature[arg] if arg in signature else None for arg in args)
        else:
            return (None,) * len(args)


def get_arginfo(obj, args):
    """get_arginfo(obj, args) return a tuple of the object argument info."""
    return ('arg_info',) * len(args)
