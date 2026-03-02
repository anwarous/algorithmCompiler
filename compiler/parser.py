from __future__ import annotations

from typing import List, Sequence

from compiler.ast_nodes import (
    Assignment,
    BinaryOp,
    Block,
    Identifier,
    If,
    IntegerLiteral,
    Program,
    Read,
    RealLiteral,
    StringLiteral,
    UnaryOp,
    While,
    Write,
)
from compiler.lexer import Token


class ParseError(Exception):
    pass


class Parser:
    def __init__(self, tokens: Sequence[Token]):
        self.tokens = list(tokens)
        self.pos = 0

    def parse_program(self) -> Program:
        alg = self._consume("ALGORITHME", "Expected 'Algorithme' at program start")
        name = self._consume("IDENT", "Expected algorithm name after 'Algorithme'")
        self._consume("DEBUT", "Expected 'Début' before statements")
        body = self._parse_block(stop_tokens={"FIN"})
        self._consume("FIN", "Expected 'Fin' at end of algorithm")
        self._consume("EOF", "Unexpected tokens after program end")
        return Program(line=alg.line, name=name.value, body=body)

    def _parse_block(self, stop_tokens: set[str]) -> Block:
        stmts = []
        start = self._peek().line
        while self._peek().kind not in stop_tokens:
            stmts.append(self._parse_statement())
        return Block(line=start, statements=stmts)

    def _parse_statement(self):
        tok = self._peek()
        if tok.kind == "IDENT":
            return self._parse_assignment()
        if tok.kind == "LIRE":
            return self._parse_read()
        if tok.kind == "ECRIRE":
            return self._parse_write()
        if tok.kind == "TANTQUE":
            return self._parse_while()
        if tok.kind == "SI":
            return self._parse_if()
        raise ParseError(f"Unexpected token '{tok.value or tok.kind}' at line {tok.line}, column {tok.column}")

    def _parse_assignment(self) -> Assignment:
        ident = self._consume("IDENT", "Expected identifier")
        self._consume("ASSIGN", "Expected '<-' in assignment")
        expr = self._parse_expression()
        return Assignment(line=ident.line, target=ident.value, value=expr)

    def _parse_read(self) -> Read:
        lire = self._consume("LIRE", "Expected 'Lire'")
        self._consume("LPAREN", "Expected '(' after Lire")
        ident = self._consume("IDENT", "Expected identifier in Lire")
        self._consume("RPAREN", "Expected ')' after Lire argument")
        return Read(line=lire.line, target=ident.value)

    def _parse_write(self) -> Write:
        write = self._consume("ECRIRE", "Expected 'Écrire'")
        self._consume("LPAREN", "Expected '(' after Écrire")
        values = [self._parse_expression()]
        while self._match("COMMA"):
            values.append(self._parse_expression())
        self._consume("RPAREN", "Expected ')' after Écrire arguments")
        return Write(line=write.line, values=values)

    def _parse_while(self) -> While:
        start = self._consume("TANTQUE", "Expected 'TantQue'")
        self._consume("LPAREN", "Expected '(' after TantQue")
        cond = self._parse_expression()
        self._consume("RPAREN", "Expected ')' after TantQue condition")
        self._consume("FAIRE", "Expected 'Faire' after TantQue condition")
        body = self._parse_block(stop_tokens={"FINTANTQUE"})
        self._consume("FINTANTQUE", "Expected 'FinTantQue' after loop body")
        return While(line=start.line, condition=cond, body=body)

    def _parse_if(self) -> If:
        start = self._consume("SI", "Expected 'Si'")
        self._consume("LPAREN", "Expected '(' after Si")
        cond = self._parse_expression()
        self._consume("RPAREN", "Expected ')' after Si condition")
        self._consume("ALORS", "Expected 'Alors' after condition")
        then_block = self._parse_block(stop_tokens={"SINON", "FINSI"})
        else_block = None
        if self._match("SINON"):
            else_block = self._parse_block(stop_tokens={"FINSI"})
        self._consume("FINSI", "Expected 'FinSi' to close if")
        return If(line=start.line, condition=cond, then_block=then_block, else_block=else_block)

    def _parse_expression(self):
        return self._parse_equality()

    def _parse_equality(self):
        expr = self._parse_comparison()
        while self._peek().kind in {"EQ", "NE"}:
            op = self._advance()
            right = self._parse_comparison()
            expr = BinaryOp(line=op.line, op=op.kind, left=expr, right=right)
        return expr

    def _parse_comparison(self):
        expr = self._parse_term()
        while self._peek().kind in {"LT", "LE", "GT", "GE"}:
            op = self._advance()
            right = self._parse_term()
            expr = BinaryOp(line=op.line, op=op.kind, left=expr, right=right)
        return expr

    def _parse_term(self):
        expr = self._parse_factor()
        while self._peek().kind in {"PLUS", "MINUS"}:
            op = self._advance()
            right = self._parse_factor()
            expr = BinaryOp(line=op.line, op=op.kind, left=expr, right=right)
        return expr

    def _parse_factor(self):
        expr = self._parse_unary()
        while self._peek().kind in {"STAR", "SLASH", "MOD", "DIV"}:
            op = self._advance()
            right = self._parse_unary()
            expr = BinaryOp(line=op.line, op=op.kind, left=expr, right=right)
        return expr

    def _parse_unary(self):
        if self._peek().kind == "MINUS":
            op = self._advance()
            operand = self._parse_unary()
            return UnaryOp(line=op.line, op=op.kind, operand=operand)
        return self._parse_primary()

    def _parse_primary(self):
        tok = self._peek()
        if tok.kind == "INTEGER":
            self._advance()
            return IntegerLiteral(line=tok.line, value=int(tok.value))
        if tok.kind == "REAL":
            self._advance()
            return RealLiteral(line=tok.line, value=float(tok.value))
        if tok.kind == "STRING":
            self._advance()
            return StringLiteral(line=tok.line, value=tok.value)
        if tok.kind == "IDENT":
            self._advance()
            return Identifier(line=tok.line, name=tok.value)
        if tok.kind == "LPAREN":
            self._advance()
            expr = self._parse_expression()
            self._consume("RPAREN", "Expected ')' after expression")
            return expr
        raise ParseError(f"Unexpected token '{tok.value or tok.kind}' in expression at line {tok.line}, column {tok.column}")

    def _peek(self) -> Token:
        return self.tokens[self.pos]

    def _advance(self) -> Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def _match(self, kind: str) -> bool:
        if self._peek().kind == kind:
            self._advance()
            return True
        return False

    def _consume(self, kind: str, message: str) -> Token:
        if self._peek().kind == kind:
            return self._advance()
        got = self._peek()
        raise ParseError(f"{message} at line {got.line}, column {got.column}; got '{got.value or got.kind}'")
