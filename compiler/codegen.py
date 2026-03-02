from __future__ import annotations

from typing import Dict, List

from compiler import ast_nodes as ast


class CodeGenerator:
    C_TYPES = {"int": "int", "real": "double", "string": "char*", "bool": "int"}

    def __init__(self, symbols: Dict[str, str]):
        self.symbols = symbols

    def generate(self, program: ast.Program) -> str:
        lines = ["#include <stdio.h>", "", "int main() {"]
        decl = self._emit_declarations()
        if decl:
            lines.extend([f"    {line}" for line in decl])
        for stmt in program.body.statements:
            lines.extend(self._stmt(stmt, 1))
        lines.append("    return 0;")
        lines.append("}")
        return "\n".join(lines) + "\n"

    def _emit_declarations(self) -> List[str]:
        by_type: Dict[str, List[str]] = {}
        for name, typ in sorted(self.symbols.items()):
            by_type.setdefault(typ, []).append(name)
        return [f"{self.C_TYPES[typ]} {', '.join(names)};" for typ, names in by_type.items()]

    def _stmt(self, stmt: ast.Statement, indent: int) -> List[str]:
        p = "    " * indent
        if isinstance(stmt, ast.Assignment):
            return [f"{p}{stmt.target} = {self._expr(stmt.value)};"]
        if isinstance(stmt, ast.Read):
            typ = self.symbols[stmt.target]
            fmt = "%d" if typ in {"int", "bool"} else "%lf"
            return [f"{p}scanf(\"{fmt}\", &{stmt.target});"]
        if isinstance(stmt, ast.Write):
            return self._write_stmt(stmt, indent)
        if isinstance(stmt, ast.While):
            lines = [f"{p}while ({self._expr(stmt.condition)}) {{"]
            for inner in stmt.body.statements:
                lines.extend(self._stmt(inner, indent + 1))
            lines.append(f"{p}}}")
            return lines
        if isinstance(stmt, ast.If):
            lines = [f"{p}if ({self._expr(stmt.condition)}) {{"]
            for inner in stmt.then_block.statements:
                lines.extend(self._stmt(inner, indent + 1))
            if stmt.else_block:
                lines.append(f"{p}}} else {{")
                for inner in stmt.else_block.statements:
                    lines.extend(self._stmt(inner, indent + 1))
            lines.append(f"{p}}}")
            return lines
        raise ValueError(f"Unsupported statement: {stmt}")

    def _write_stmt(self, stmt: ast.Write, indent: int) -> List[str]:
        p = "    " * indent
        fmt_parts, args = [], []
        for val in stmt.values:
            t = val.inferred_type
            if t == "string":
                if isinstance(val, ast.StringLiteral):
                    fmt_parts.append(val.value)
                else:
                    fmt_parts.append("%s")
                    args.append(self._expr(val))
            elif t in {"int", "bool"}:
                fmt_parts.append("%d")
                args.append(self._expr(val))
            elif t == "real":
                fmt_parts.append("%g")
                args.append(self._expr(val))
            else:
                raise ValueError(f"Unsupported print type: {t}")
        fmt = "".join(fmt_parts) + "\n"
        if args:
            return [f'{p}printf("{self._escape(fmt)}", {", ".join(args)});']
        return [f'{p}printf("{self._escape(fmt)}");']

    @staticmethod
    def _escape(text: str) -> str:
        return text.replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')

    def _expr(self, expr: ast.Expression) -> str:
        if isinstance(expr, ast.IntegerLiteral):
            return str(expr.value)
        if isinstance(expr, ast.RealLiteral):
            return str(expr.value)
        if isinstance(expr, ast.StringLiteral):
            return f'"{self._escape(expr.value)}"'
        if isinstance(expr, ast.Identifier):
            return expr.name
        if isinstance(expr, ast.UnaryOp):
            return f"(-{self._expr(expr.operand)})"
        if isinstance(expr, ast.BinaryOp):
            op = {
                "PLUS": "+",
                "MINUS": "-",
                "STAR": "*",
                "SLASH": "/",
                "DIV": "/",
                "MOD": "%",
                "EQ": "==",
                "NE": "!=",
                "LT": "<",
                "LE": "<=",
                "GT": ">",
                "GE": ">=",
            }[expr.op]
            return f"({self._expr(expr.left)} {op} {self._expr(expr.right)})"
        raise ValueError(f"Unsupported expression: {expr}")
