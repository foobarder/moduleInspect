import pandas
import os
from extractiontools import (Module, get_name, get_doc_string, get_prefix,
                             strip_text, get_argnames, get_argtypes,
                             get_argdefvalues, get_arginfo)


def join_members(*members):
    """join_memebers(member1, ...) takes an orbitrary number of
    arguments of type 'str'and concatinates them with using the '.' separator"""
    return '.'.join(members)


def merge(dictionaryA, dictionaryB):
    """merge(dict_A, dict_B) merges two dictionaries"""
    d = dictionaryA.copy()
    d.update(dictionaryB)
    return d


def generate_documentation(module_name):
    """generate_documentation(module_name) return a dictionary containing information about the module functions and methods"""
    module = Module(module_name)
    doc_frame = {'module_name': module_name,
                 'module_version': module.get_module_version(),
                 'full_name': [],
                 'prefix': [],
                 'function_name': [],
                 'function_doc': [],
                 'argument': [],
                 'argument_default_value': [],
                 'argument_type': [],
                 'argument_info': []}

    for member_name, member in merge(module.functions, module.class_methods).items():
        doc_frame['full_name'].append(member_name)
        doc_frame['prefix'].append(get_prefix(member_name))
        doc_frame['function_name'].append(get_name(member))
        doc_frame['function_doc'].append(get_doc_string(member))
        doc_frame['argument'].append(get_argnames(member))
        doc_frame['argument_default_value'].append(get_argdefvalues(member, doc_frame['argument'][-1]))
        doc_frame['argument_type'].append(get_argtypes(member, doc_frame['argument_default_value'][-1]))
        doc_frame['argument_info'].append(get_arginfo(member, doc_frame['argument'][-1]))
    return doc_frame


def main(module_name):
    index = ['module_name', 'module_version', 'full_name', 'prefix', 'function_name', 'function_doc']

    def expand(x):
        y = pandas.DataFrame(x.values.tolist())
        return y.stack()

    def format_frame(frame, index):
        level_to_drop = 'level_{}'.format(len(index))
        formated_frame = frame.set_index(index).apply(lambda x: expand(x), 1).stack(dropna=False).reset_index().drop(level_to_drop, 1)
        formated_frame.columns = index + [x for x in frame.columns if x not in index]
        return formated_frame

    doc_frame = generate_documentation(module_name)
    dframe = format_frame(pandas.DataFrame(doc_frame), index)
    dframe.to_csv(os.path.join(os.getcwd(), join_members(module_name, 'csv')), index=False)


if __name__ == "__main__":
    main('numpy')
