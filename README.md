# French Pseudo-code Compiler → C

This project implements a full compiler that translates French-style pseudo-code into executable C.

## Architecture

The compiler pipeline is split into modules:

- `compiler/lexer.py`: lexical analyzer (keywords, identifiers, numbers, strings, operators, comments).
- `compiler/parser.py`: recursive-descent parser building an AST.
- `compiler/ast_nodes.py`: AST node definitions.
- `compiler/semantic.py`: semantic analysis, variable type inference, type checking, undeclared variable checks.
- `compiler/codegen.py`: C code generation (`while`, `if/else`, `printf`, `scanf`, `%`, `/`).
- `compile.py`: CLI entry point.

## Supported Grammar (EBNF)

```ebnf
program      := "Algorithme" IDENT "Début" block "Fin" ;
block        := { statement } ;
statement    := assignment
              | read
              | write
              | while
              | if ;
assignment   := IDENT "<-" expression ;
read         := "Lire" "(" IDENT ")" ;
write        := "Écrire" "(" expression { "," expression } ")" ;
while        := "TantQue" "(" expression ")" "Faire" block "FinTantQue" ;
if           := "Si" "(" expression ")" "Alors" block [ "Sinon" block ] "FinSi" ;
expression   := equality ;
equality     := comparison { ("=" | "!=") comparison } ;
comparison   := term { ("<" | "<=" | ">" | ">=") term } ;
term         := factor { ("+" | "-") factor } ;
factor       := unary { ("*" | "/" | "Mod" | "Div") unary } ;
unary        := ["-"] primary ;
primary      := INTEGER | REAL | STRING | IDENT | "(" expression ")" ;
```

## Translation Rules

- `TantQue (...) Faire ... FinTantQue` → `while (...) { ... }`
- `Si ... Alors ... Sinon ... FinSi` → `if (...) { ... } else { ... }`
- `Lire(x)` → `scanf(...)` using inferred type.
- `Écrire(...)` → `printf(...)` with inferred format string.
- `Mod` → `%`
- `Div` → `/`

## Type System and Semantic Checks

- Types supported: `int`, `real`, `string`, `bool` (internal for comparisons).
- Variables are auto-declared when first assigned/read.
- Assignment compatibility:
  - exact type match allowed
  - `int` → `real` promotion allowed
- Errors reported for:
  - undeclared identifier usage in expressions
  - illegal arithmetic (`string` in arithmetic)
  - non-integer `Mod` / `Div`
  - incompatible assignment types
  - invalid condition type in `Si`/`TantQue`

## Comments

Single-line comments are supported with `#`.

## Usage

Generate C code:

```bash
python3 compile.py examples/inverse.alg -o generated/inverse.c
python3 compile.py examples/parite_signe.alg -o generated/parite_signe.c
```


Quick one-command flow with helper script:

```bash
./run.sh examples/inverse.alg
./run.sh examples/parite_signe.alg
```

You can also override binary name:

```bash
./run.sh examples/inverse.alg inverse_custom
```

Compile generated C code:

```bash
gcc generated/inverse.c -o generated/inverse
./generated/inverse

gcc generated/parite_signe.c -o generated/parite_signe
./generated/parite_signe
```

## Example Inputs

- `examples/inverse.alg`
- `examples/parite_signe.alg`

## Generated Outputs

- `generated/inverse.c`
- `generated/parite_signe.c`
