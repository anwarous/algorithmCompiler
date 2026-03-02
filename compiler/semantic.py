from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from compiler import ast_nodes as ast


class SemanticError(Exception):
    pass


@dataclass
class SemanticResult:
    symbols: Dict[str, str]


class SemanticAnalyzer:
    def __init__(self):
        self.symbols: Dict[str, str] = {}

    def analyze(self, program: ast.Program) -> SemanticResult:
        self._check_block(program.body)
        return SemanticResult(symbols=self.symbols)

    def _check_block(self, block: ast.Block) -> None:
        for stmt in block.statements:
            self._check_stmt(stmt)

    def _check_stmt(self, stmt: ast.Statement):
        if isinstance(stmt, ast.Assignment):
            rhs_type = self._expr_type(stmt.value)
            existing = self.symbols.get(stmt.target)
            if existing is None:
                self.symbols[stmt.target] = rhs_type
            elif not self._is_assignable(existing, rhs_type):
                raise SemanticError(
                    f"Type mismatch at line {stmt.line}: cannot assign {rhs_type} to variable '{stmt.target}' of type {existing}"
                )
        elif isinstance(stmt, ast.Read):
            if stmt.target not in self.symbols:
                self.symbols[stmt.target] = "int"
        elif isinstance(stmt, ast.Write):
            for value in stmt.values:
                self._expr_type(value)
        elif isinstance(stmt, ast.While):
            cond_t = self._expr_type(stmt.condition)
            if cond_t not in {"int", "real", "bool"}:
                raise SemanticError(f"Invalid while condition type '{cond_t}' at line {stmt.line}")
            self._check_block(stmt.body)
        elif isinstance(stmt, ast.If):
            cond_t = self._expr_type(stmt.condition)
            if cond_t not in {"int", "real", "bool"}:
                raise SemanticError(f"Invalid if condition type '{cond_t}' at line {stmt.line}")
            self._check_block(stmt.then_block)
            if stmt.else_block:
                self._check_block(stmt.else_block)
        else:
            raise SemanticError(f"Unsupported statement at line {stmt.line}")

    def _expr_type(self, expr: ast.Expression) -> str:
        if isinstance(expr, ast.IntegerLiteral):
            expr.inferred_type = "int"
            return "int"
        if isinstance(expr, ast.RealLiteral):
            expr.inferred_type = "real"
            return "real"
        if isinstance(expr, ast.StringLiteral):
            expr.inferred_type = "string"
            return "string"
        if isinstance(expr, ast.Identifier):
            if expr.name not in self.symbols:
                raise SemanticError(f"Undeclared variable '{expr.name}' at line {expr.line}")
            expr.inferred_type = self.symbols[expr.name]
            return expr.inferred_type
        if isinstance(expr, ast.UnaryOp):
            operand_t = self._expr_type(expr.operand)
            if expr.op == "MINUS" and operand_t in {"int", "real"}:
                expr.inferred_type = operand_t
                return operand_t
            raise SemanticError(f"Unsupported unary operation at line {expr.line}")
        if isinstance(expr, ast.BinaryOp):
            l_t = self._expr_type(expr.left)
            r_t = self._expr_type(expr.right)
            if expr.op in {"PLUS", "MINUS", "STAR", "SLASH", "DIV", "MOD"}:
                if l_t == "string" or r_t == "string":
                    raise SemanticError(f"Illegal arithmetic on string at line {expr.line}")
                if expr.op in {"DIV", "MOD"} and (l_t != "int" or r_t != "int"):
                    raise SemanticError(f"'{expr.op}' requires integer operands at line {expr.line}")
                result = "real" if "real" in {l_t, r_t} and expr.op not in {"DIV", "MOD"} else "int"
                expr.inferred_type = result
                return result
            if expr.op in {"EQ", "NE", "LT", "LE", "GT", "GE"}:
                if "string" in {l_t, r_t} and l_t != r_t:
                    raise SemanticError(f"Cannot compare {l_t} and {r_t} at line {expr.line}")
                expr.inferred_type = "bool"
                return "bool"
        raise SemanticError(f"Unsupported expression at line {expr.line}")

    @staticmethod
    def _is_assignable(dest: str, src: str) -> bool:
        return dest == src or (dest == "real" and src == "int")
