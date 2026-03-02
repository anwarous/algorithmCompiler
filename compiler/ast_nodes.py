from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Union


@dataclass
class Node:
    line: int


@dataclass
class Program(Node):
    name: str
    body: "Block"


@dataclass
class Block(Node):
    statements: List["Statement"] = field(default_factory=list)


class Statement(Node):
    pass


class Expression(Node):
    inferred_type: Optional[str] = None


@dataclass
class Assignment(Statement):
    target: str
    value: Expression


@dataclass
class Read(Statement):
    target: str


@dataclass
class Write(Statement):
    values: List[Expression]


@dataclass
class While(Statement):
    condition: Expression
    body: Block


@dataclass
class If(Statement):
    condition: Expression
    then_block: Block
    else_block: Optional[Block]


@dataclass
class BinaryOp(Expression):
    op: str
    left: Expression
    right: Expression


@dataclass
class UnaryOp(Expression):
    op: str
    operand: Expression


@dataclass
class Identifier(Expression):
    name: str


@dataclass
class IntegerLiteral(Expression):
    value: int


@dataclass
class RealLiteral(Expression):
    value: float


@dataclass
class StringLiteral(Expression):
    value: str


StatementType = Union[Assignment, Read, Write, While, If]
ExpressionType = Union[BinaryOp, UnaryOp, Identifier, IntegerLiteral, RealLiteral, StringLiteral]
