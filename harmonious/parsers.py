def parse_variable(var):
    parts = var.split("=")
    if len(parts) > 0:
        return (parts[0], unquote_variable(parts[1]))
    else:
        return var

def unquote_variable(name):
    UNQUOTABLE_CHARS = ["\"", "'", "[", "]"]
    if name[0] in UNQUOTABLE_CHARS and name[-1] in UNQUOTABLE_CHARS:
        return name[1:-1]
    else:
        return name

def is_substitution(name):
    return name[0] == "[" and name[-1] == "]"