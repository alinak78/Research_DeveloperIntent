"""Read JSON from stdin, screen a narrow Python subset, and evaluate synthetic cases.

Must be launched through candidate.sb by the experiment runner. No network or API code.
"""
import ast
import contextlib
import io
import json
import resource
import sys

SAFE_BUILTINS = {k: v for k, v in vars(__builtins__).items() if k in {
    'len','str','int','float','bool','list','dict','set','tuple','enumerate','range',
    'zip','sorted','reversed','min','max','sum','any','all','isinstance','abs',
    'Exception','ValueError','TypeError','KeyError','IndexError','None',
}}
SAFE_ATTRS = {'strip','lstrip','rstrip','lower','upper','get','items','keys','values',
              'copy','append','extend','add','discard','remove','pop','setdefault','update','count'}
DISALLOWED = (ast.Import, ast.ImportFrom, ast.ClassDef, ast.AsyncFunctionDef,
              ast.Global, ast.Nonlocal, ast.With, ast.AsyncWith, ast.Await,
              ast.Yield, ast.YieldFrom, ast.Delete)


def screen(source):
    tree = ast.parse(source)
    if not tree.body or any(not isinstance(n, ast.FunctionDef) for n in tree.body):
        raise ValueError('Only function definitions are accepted at module level')
    if not any(n.name == 'solution' for n in tree.body):
        raise ValueError('Missing solution function')
    for node in ast.walk(tree):
        if isinstance(node, DISALLOWED):
            raise ValueError('Unsupported syntax: '+type(node).__name__)
        if isinstance(node, ast.Name) and (node.id.startswith('_') or node.id in {
            'open','eval','exec','compile','globals','locals','vars','dir','getattr','setattr','delattr','input','breakpoint','help','memoryview','type','object','super',
        }):
            raise ValueError('Unsupported name')
        if isinstance(node, ast.Attribute) and node.attr not in SAFE_ATTRS:
            raise ValueError('Unsupported attribute')
        if isinstance(node, ast.FunctionDef):
            if node.decorator_list or node.returns or node.name.startswith('_') or node.args.defaults or node.args.kw_defaults:
                raise ValueError('Decorators, annotations and default arguments unsupported')
            if any(arg.annotation for arg in node.args.args):
                raise ValueError('Annotations unsupported')
    return tree


def main():
    resource.setrlimit(resource.RLIMIT_CPU, (2, 2))
    # RLIMIT_AS is not consistently enforced by macOS; sandbox and timeouts remain required.
    try:
        resource.setrlimit(resource.RLIMIT_AS, (768*1024*1024, 768*1024*1024))
    except (ValueError, OSError):
        pass
    data = json.loads(sys.stdin.read())
    try:
        tree = screen(data['source'])
    except (ValueError, SyntaxError) as e:
        print(json.dumps({'status':'rejected','reason':str(e)[:180]}))
        return
    namespace = {'__builtins__': SAFE_BUILTINS}
    outcomes = []
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            exec(compile(tree, '<candidate>', 'exec'), namespace)
            for case in data['cases']:
                try:
                    rows = json.loads(json.dumps(case['rows']))
                    output = namespace['solution'](rows, case['allowed'])
                    json.dumps(output)  # Require a JSON-compatible return value.
                    outcomes.append({'status':'ok','output':output})
                except BaseException as e:
                    outcomes.append({'status':'error','error_type':type(e).__name__})
        print(json.dumps({'status':'evaluated','cases':outcomes}))
    except BaseException as e:
        print(json.dumps({'status':'error','error_type':type(e).__name__}))


if __name__ == '__main__':
    main()
