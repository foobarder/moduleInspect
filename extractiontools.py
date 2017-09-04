from importlib import import_module
from pkgutil import walk_packages
import operator
import inspect
import pydoc
import sys
import re
from mergetools import join_members


class Module:
    def __init__(self, module_name):
        self.module_name = module_name
        self.module = import_module(self.module_name)

        self.submodules = self.get_submodules()
        self.functions = self.get_functions()
        self.classes = self.get_classes()
        self.class_methods = self.get_class_methods()

    def get_module_version(self):
        return self.module.__version__

    def get_submodules(self):
        submodules = {}
        for loader, name, is_pkg in walk_packages(self.module.__path__, self.module.__name__ + '.'):
            if self.is_imported(name):
                submodules[name] = self.get_submodule(self.get_mlattr(name))
        return submodules

    def get_functions(self):
        functions = {}
        for submodule_name, submodule in self.submodules.items():
            for function_name, function in inspect.getmembers(submodule, lambda f: inspect.isfunction(f) or inspect.isbuiltin(f)):
                functions[join_members(submodule_name, function_name)] = function
        return functions

    def get_classes(self):
        classes = {}
        for submodule_name, submodule in self.submodules.items():
            for class_name, class_ in inspect.getmembers(submodule, lambda c: inspect.isclass(c)):
                classes[join_members(submodule_name, class_name)] = class_
        return classes

    def get_class_methods(self):
        methods = {}
        for class_name, class_ in self.classes.items():
            for method_name, method in inspect.getmembers(class_, lambda m: inspect.ismethod(m) or inspect.isbuiltin(m)):
                methods[join_members(class_name, method_name)] = method
        return methods

    def is_imported(self, name):
        return name in sys.modules

    def get_mlattr(self, full_name):
        return full_name.split('.', 1)[1]

    def get_submodule(self, attr):
        return operator.attrgetter(attr)(self.module)


def get_name(obj):
    return obj.__name__


def get_doc_string(obj):
    return re.sub('\x08.', '', pydoc.render_doc(obj)) or obj.__doc__


def get_prefix(name):
    return name.split('.', 1)[1].rsplit('.', 1)[0]


def strip_text(string):
    return re.sub('\x08.', '', string.replace('\n', ''))


def get_argnames(obj):
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
    return ('arg_type',) * len(defaults)


def get_argdefvalues(obj, args):
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
    return ('arg_info',) * len(args)
