def unquote_variable(name):
    unquotable_chars = ["\"", "'", "[", "]"]
    if name[0] in unquotable_chars and name[-1] in unquotable_chars:
        return name[1:-1]
    else:
        return name


def is_substitution(name):
    return name[0] == "[" and name[-1] == "]"