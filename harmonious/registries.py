import re
from collections import defaultdict

class DirectiveRegistry(dict):
    def add_directive(self, regexp, dir_func):
        self[re.compile(regexp, flags=re.IGNORECASE)] = dir_func

DIRECTIVE_REGISTRY = DirectiveRegistry()
TASK_REGISTRY = defaultdict(lambda: None)