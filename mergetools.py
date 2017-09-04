def join_members(*members):
    """join_memebers(member1, ...) takes an orbitrary number of
    arguments of type 'str'and concatinates them with using the '.' separator"""
    return '.'.join(members)


def merge(dictionaryA, dictionaryB):
    """merge(dict_A, dict_B) merges two dictionaries"""
    d = dictionaryA.copy()
    d.update(dictionaryB)
    return d
