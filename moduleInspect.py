from importlib import import_module
from pkgutil import walk_packages
import operator
import inspect
import sys


def join_members(*members):
    return '.'.join(members)


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
            for function_name, function in inspect.getmembers(submodule, lambda f: inspect.isfunction(f)):
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
            for method_name, method in inspect.getmembers(class_, lambda m: inspect.ismethod(m)):
                methods[join_members(class_name, method_name)] = method
        return methods

    def is_imported(self, name):
        return name in sys.modules

    def get_mlattr(self, full_name):
        return full_name.split('.', 1)[1]

    def get_submodule(self, attr):
        return operator.attrgetter(attr)(self.module)


if __name__ == "__main__":
    module = Module('numpy')
