def join_members(*members):
    return '.'.join(members)


def merge(dictionaryA, dictionaryB):
    d = dictionaryA.copy()
    d.update(dictionaryB)
    return d
