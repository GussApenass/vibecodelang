# Codex Prompt — Design and Implementation of “VibeCodeLang”

You are tasked with designing and implementing a new programming language called **VibeCodeLang** (`.vb`) and its full interpreter + CLI tool.

This language is a hybrid between:
- TypeScript (strong static typing, interfaces, types, expressive syntax)
- C (memory control concepts, low-level awareness, explicit behavior control)

It is designed to be **extremely type-safe, predictable, and expressive**, while still being fun and modern.

---

# 🚀 Core Goals

Build a complete programming language system that includes:

1. A custom language (`.vb`)
2. A fully working interpreter (Python preferred)
3. A CLI tool: `vibecoded`
4. Config system via `vbconfigs.json`
5. Error system with Python-like clarity
6. Example programs in `examples/`

---

# 🧠 Language Philosophy

- Strong static typing (mandatory in most cases)
- Explicit variable declarations
- Simple but expressive syntax
- Memory-aware behavior inspired by C (conceptual, not full manual pointers required)
- Clean, readable execution model
- Designed for learning + experimentation + tooling + AI agents

---

# 📜 Syntax Specification

## Variables

```vb
var name: string > "hello world"
var age: number > 20
````

Type is mandatory unless explicitly configured otherwise.

---

## Functions

```vb
function sum[a: number, b: number] > number {
    return a + b
}
```

Function return types are required.

---

## Function usage

```vb
var result: number > sum(1, 3)
```

---

## Output

```vb
out("Hello world")
out("Result is @{result}")
```

---

## Conditionals

```vb
if [name == "john"] {
    out("hello john")
} elseif [name == "admin"] {
    out("welcome admin")
} else {
    out("unknown user")
}
```

---

## Input

```vb
var value: string > outinput("Enter a value: ")
out(value)
```

---

## Loops

### For loop

```vb
for [i: number = 0; i < 10; i = i + 1] {
    out(i)
}
```

### While loop

```vb
while [x < 10] {
    x = x + 1
}
```

---

## Interfaces

```vb
interface > User [
    name: string
    age: number
]
```

---

## Types

```vb
type ID > number
type Username > string
```

---

# ⚙️ Language Features

## Must implement:

* Static type checking (before execution or during AST phase)
* Runtime type validation fallback
* Variable scope handling (block scoped)
* Function scope isolation
* String interpolation with `@{}` syntax
* Basic arithmetic operations
* Comparison operators
* Logical operators

---

# 🧱 Interpreter Requirements (Python preferred)

Implement a full interpreter with:

### Architecture:

* Lexer
* Parser (AST generation)
* Interpreter (execution engine)
* Error handler system

### Must support:

* Tokenization of `.vb`
* AST-based execution
* Variable environment (stack-based or dictionary-based scopes)
* Function registry
* Type validation system

---

# 🧨 Error System

Errors must be:

* Clear like Python
* Include:

  * File name
  * Line number
  * Column (optional but recommended)
  * Error message

Example:

```
VibeCodeError: Type mismatch

File: main.vb
Line: 3

Expected type 'number' but got 'string'
```

---

# 🖥️ CLI Tool

The CLI command must be:

```bash
vibecoded <file>.vb
```

### Optional commands via config:

```bash
vibecoded run dev
vibecoded run start
```

These are defined in `vbconfigs.json`.

---

# ⚙️ Configuration File

File: `vbconfigs.json`

Example:

```json
{
  "commands": {
    "dev": "vibecoded test.vb",
    "start": "vibecoded production.vb"
  },
  "strictMode": true,
  "allowImplicitTypes": false
}
```

---

# 📁 Project Structure

Create the project structure in a way you find most appropriate and maintainable.

Make sure to include a `README.md` file that clearly explains how to install, configure, and use the language and CLI tool.

Also, include an `examples/` directory containing multiple `.vb` example files demonstrating different language features such as variables, functions, loops, conditionals, and interfaces.

Additionally, ensure there is a `vbconfigs.json` configuration file properly integrated into the project, showcasing how users can customize the interpreter behavior and define CLI commands.

The overall structure should be clean, scalable, and easy to understand for new developers contributing to or using the project.

# 🧠 Advanced Requirements

* Ensure extensibility for future features:

  * Modules/imports
  * Package system
  * Async functions (future support)
* Design AST in a way that supports plugins
* Keep interpreter modular

---

# 🎯 Final Instruction

Build everything from scratch, clean, maintainable, and well-commented.

Focus on:

* Robust parsing
* Clear interpreter design
* Good developer experience
* Strong error reporting
* Extensibility

This is not a toy — it should feel like a real programming language foundation.