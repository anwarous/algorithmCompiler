#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from compiler.codegen import CodeGenerator
from compiler.lexer import LexError, Lexer
from compiler.parser import ParseError, Parser
from compiler.semantic import SemanticAnalyzer, SemanticError


def compile_source(source: str) -> str:
    tokens = Lexer(source).tokenize()
    program = Parser(tokens).parse_program()
    semantic = SemanticAnalyzer().analyze(program)
    return CodeGenerator(semantic.symbols).generate(program)


def main() -> int:
    parser = argparse.ArgumentParser(description="French pseudo-code to C compiler")
    parser.add_argument("input", type=Path, help="Input .alg file")
    parser.add_argument("-o", "--output", type=Path, required=True, help="Output C file")
    args = parser.parse_args()

    try:
        source = args.input.read_text(encoding="utf-8")
        c_code = compile_source(source)
        args.output.write_text(c_code, encoding="utf-8")
        print(f"Generated C code: {args.output}")
        return 0
    except (LexError, ParseError, SemanticError) as exc:
        print(f"Compilation error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
