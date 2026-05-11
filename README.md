# VibeCodeLang

VibeCodeLang is a small, strongly typed experimental language with TypeScript-like declarations and C-inspired explicitness. Files use the `.vb` extension and run through the `vibecoded` CLI.

## Install

The project is pure Python and requires Python 3.10 or newer.

```bash
python -m pip install -e .
```

You can also run the local launcher directly:

```bash
./vibecoded examples/basics.vb
```

If you see `vibecoded: command not found`, either install the project with
`python -m pip install -e .` first, or run the local launcher with `./vibecoded`.
The `./` is required because shells do not search the current directory for
commands by default.

## CLI

Run a source file:

```bash
vibecoded examples/basics.vb
```

Run a configured command from `vbconfigs.json`:

```bash
vibecoded run dev
vibecoded run start
```

`vbconfigs.json` supports command aliases and language settings:

```json
{
  "commands": {
    "dev": "vibecoded examples/basics.vb",
    "start": "vibecoded examples/functions_loops.vb"
  },
  "strictMode": true,
  "allowImplicitTypes": false
}
```

## Language Quick Start

Variables require explicit types by default:

```vb
var name: string > "hello world"
var age: number > 20
```

Functions use bracketed parameter lists and explicit return types:

```vb
function sum[a: number, b: number] > number {
    return a + b
}

var result: number > sum(1, 3)
out("Result is @{result}")
```

Conditionals and loops:

```vb
if [name == "john"] {
    out("hello john")
} elseif [name == "admin"] {
    out("welcome admin")
} else {
    out("unknown user")
}

for [i: number = 0; i < 10; i = i + 1] {
    out(i)
}

while [age < 30] {
    age = age + 1
}
```

Type aliases and interfaces are registered by the interpreter so future object and tooling features can build on the AST:

```vb
type ID > number

interface > User [
    name: string
    age: number
]
```

## Implemented Features

- Lexer, parser, AST, interpreter, and CLI are separate modules.
- Static-style validation runs before variable assignment, function binding, and function returns.
- Runtime type checks validate values at execution boundaries.
- Block scoped variables with assignment lookup through outer scopes.
- Function scope isolation.
- String interpolation with `@{name}`.
- Arithmetic, comparison, and logical operators.
- Python-style error messages with file, line, column, and a focused message.

## Project Layout

```text
vibecodelang/
  ast_nodes.py
  cli.py
  config.py
  errors.py
  interpreter.py
  lexer.py
  parser.py
  runner.py
  runtime.py
  tokens.py
examples/
  basics.vb
  functions_loops.vb
  input.vb
  type_error.vb
vbconfigs.json
vibecoded
```
