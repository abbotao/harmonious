import re
from collections import defaultdict

class DirectiveRegistry(dict):
    def add_directive(self, regexp, dir_func):
        self[re.compile(regexp, flags=re.IGNORECASE)] = dir_func

class CallbackRegistry(dict):
    def run_all(self, type, callback, **kwargs):
        for cb in self[type][callback]:
            cb(**kwargs)

TASK_REGISTRY = defaultdict(lambda: None)
DIRECTIVE_REGISTRY = DirectiveRegistry()
CALLBACK_REGISTRY = CallbackRegistry({
    'all': {
        'before': [],
        'after': [],
        'before_output': [],
        'after_output': []
    },
    'testplan': {
        'before': [],
        'after': [],
        'before_output': [],
        'after_output': []
    },
    'task': {
        'before': [],
        'after': [],
        'before_output': [],
        'after_output': []
    },
    'step': {
        'before': [],
        'after': [],
        'before_output': [],
        'after_output': []
    },
    'directive': {
        'before': [],
        'after': [],
        'before_output': [],
        'after_output': []
    }
})
