"""Per-language symbol rules for the pointer checker, built on tree-sitter grammars.

@doc: docs/VerificationTools.md#71-언어-모듈
"""

from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from functools import cache

import tree_sitter
import tree_sitter_c
import tree_sitter_cpp
import tree_sitter_go
import tree_sitter_java
import tree_sitter_javascript
import tree_sitter_python
import tree_sitter_rust
import tree_sitter_typescript
from tree_sitter import Node

DEFINITION = "definition"
VALUE = "value"
NAMESPACE = "namespace"


@dataclass(frozen=True)
class Definition:
    """A symbol found in a syntax tree.

    @doc: docs/VerificationTools.md#71-언어-모듈
    """

    qualname: str
    line: int
    kind: str
    top_level: bool
    public: bool
    docstring: tuple[int, str] | None = None


@dataclass(frozen=True)
class Language:
    """A supported language: its grammar, comment node types and symbol rules.

    @doc: docs/VerificationTools.md#71-언어-모듈
    """

    name: str
    comment_types: frozenset[str]
    grammar: Callable[[], object]
    walk: Callable[[Node], list[Definition]]
    module_docstring: Callable[[Node], tuple[int, str] | None] | None = None


def parse(language: Language, source: bytes) -> tree_sitter.Tree:
    """Parse source code with the grammar of the given language.

    @doc: docs/VerificationTools.md#71-언어-모듈
    """
    return _parser(language.name).parse(source)


@cache
def _parser(name: str) -> tree_sitter.Parser:
    return tree_sitter.Parser(tree_sitter.Language(LANGUAGES[name].grammar()))


def _text(node: Node) -> str:
    return node.text.decode("utf-8")


def _line(node: Node) -> int:
    return node.start_point.row + 1


def _join(prefix: str, name: str) -> str:
    return f"{prefix}.{name}" if prefix else name


def _preambled(
    children: Iterable[Node], preamble_types: frozenset[str], comment_types: frozenset[str]
) -> Iterator[tuple[Node, int]]:
    """Yield each item with its start line, which includes preamble siblings such as attributes."""
    start = None
    for child in children:
        if child.type in comment_types:
            continue
        if child.type in preamble_types:
            start = start or _line(child)
            continue
        yield child, start or _line(child)
        start = None


# Python

_PY_COMMENTS = frozenset({"comment"})


def _walk_python(root: Node) -> list[Definition]:
    out: list[Definition] = []
    _python_body(root, "", "module", out)
    return out


def _python_body(body: Node, prefix: str, scope: str, out: list[Definition]) -> None:
    for child, start in _preambled(body.named_children, frozenset(), _PY_COMMENTS):
        node = child.child_by_field_name("definition") if child.type == "decorated_definition" else child
        if node.type in ("function_definition", "class_definition"):
            name = _text(node.child_by_field_name("name"))
            qualname = _join(prefix, name)
            block = node.child_by_field_name("body")
            out.append(
                Definition(
                    qualname, start, DEFINITION, scope == "module", not name.startswith("_"),
                    _python_docstring(block),
                )
            )
            inner = "class" if node.type == "class_definition" else "function"
            _python_body(block, qualname, inner, out)
        elif scope != "function" and node.type == "expression_statement":
            for target in _python_assigned_names(node):
                name = _text(target)
                out.append(
                    Definition(_join(prefix, name), start, VALUE, scope == "module", not name.startswith("_"))
                )


def _python_assigned_names(statement: Node) -> Iterator[Node]:
    node = statement.named_children[0] if statement.named_children else None
    while node is not None and node.type == "assignment":
        left = node.child_by_field_name("left")
        if left.type == "identifier":
            yield left
        node = node.child_by_field_name("right")


def _python_docstring(block: Node) -> tuple[int, str] | None:
    for child in block.named_children:
        if child.type == "comment":
            continue
        if child.type == "expression_statement" and child.named_child_count == 1:
            string = child.named_children[0]
            if string.type == "string" and not any(c.type == "interpolation" for c in string.named_children):
                content = next((c for c in string.named_children if c.type == "string_content"), None)
                return (_line(content), _text(content)) if content is not None else None
        return None
    return None


# JavaScript and TypeScript

_JS_COMMENTS = frozenset({"comment"})
_JS_PREAMBLE = frozenset({"decorator"})
_JS_DEFINITIONS = frozenset(
    {
        "function_declaration",
        "generator_function_declaration",
        "function_signature",
        "class_declaration",
        "abstract_class_declaration",
        "interface_declaration",
        "type_alias_declaration",
        "enum_declaration",
    }
)
_JS_NAMESPACES = frozenset({"internal_module", "module"})
_JS_CALLABLE_VALUES = frozenset(
    {"arrow_function", "function_expression", "function", "generator_function", "class"}
)
_JS_MEMBER_DEFINITIONS = frozenset({"method_definition", "method_signature", "abstract_method_signature"})
_JS_MEMBER_VALUES = frozenset({"public_field_definition", "field_definition", "property_signature"})


def _walk_js(root: Node) -> list[Definition]:
    out: list[Definition] = []
    _js_statements(root, "", out)
    return out


def _js_statements(parent: Node, prefix: str, out: list[Definition]) -> None:
    for child, start in _preambled(parent.named_children, _JS_PREAMBLE, _JS_COMMENTS):
        _js_statement(child, start, prefix, False, out)


def _js_statement(node: Node, start: int, prefix: str, exported: bool, out: list[Definition]) -> None:
    if node.type == "export_statement":
        declaration = node.child_by_field_name("declaration")
        if declaration is not None:
            _js_statement(declaration, start, prefix, True, out)
        return
    if node.type in ("expression_statement", "ambient_declaration"):
        for child in node.named_children:
            _js_statement(child, start, prefix, exported, out)
        return
    if node.type in ("lexical_declaration", "variable_declaration"):
        for declarator in node.named_children:
            name = declarator.child_by_field_name("name") if declarator.type == "variable_declarator" else None
            if name is None or name.type != "identifier":
                continue
            value = declarator.child_by_field_name("value")
            kind = DEFINITION if value is not None and value.type in _JS_CALLABLE_VALUES else VALUE
            out.append(Definition(_join(prefix, _text(name)), start, kind, True, exported))
        return
    name = node.child_by_field_name("name")
    if name is None:
        return
    body = node.child_by_field_name("body")
    if node.type in _JS_NAMESPACES:
        qualname = _join(prefix, _text(name).strip("'\""))
        out.append(Definition(qualname, start, NAMESPACE, True, exported))
        if body is not None:
            _js_statements(body, qualname, out)
    elif node.type in _JS_DEFINITIONS:
        qualname = _join(prefix, _text(name))
        out.append(Definition(qualname, start, DEFINITION, True, exported))
        if body is None:
            return
        if node.type == "enum_declaration":
            _js_enum_members(body, qualname, out)
        else:
            _js_members(body, qualname, out)


def _js_members(body: Node, prefix: str, out: list[Definition]) -> None:
    for member, start in _preambled(body.named_children, _JS_PREAMBLE, _JS_COMMENTS):
        name = member.child_by_field_name("name") or member.child_by_field_name("property")
        if name is None:
            continue
        if member.type in _JS_MEMBER_DEFINITIONS:
            out.append(Definition(_join(prefix, _text(name)), start, DEFINITION, False, False))
        elif member.type in _JS_MEMBER_VALUES:
            out.append(Definition(_join(prefix, _text(name)), start, VALUE, False, False))


def _js_enum_members(body: Node, prefix: str, out: list[Definition]) -> None:
    for member in body.named_children:
        name = member if member.type == "property_identifier" else member.child_by_field_name("name")
        if member.type in ("property_identifier", "enum_assignment") and name is not None:
            out.append(Definition(_join(prefix, _text(name)), _line(member), VALUE, False, False))


# Rust

_RUST_COMMENTS = frozenset({"line_comment", "block_comment"})
_RUST_PREAMBLE = frozenset({"attribute_item"})
_RUST_KINDS = {
    "function_item": DEFINITION,
    "function_signature_item": DEFINITION,
    "struct_item": DEFINITION,
    "enum_item": DEFINITION,
    "union_item": DEFINITION,
    "trait_item": DEFINITION,
    "type_item": DEFINITION,
    "macro_definition": DEFINITION,
    "const_item": VALUE,
    "static_item": VALUE,
    "associated_type": VALUE,
    "mod_item": NAMESPACE,
}


def _walk_rust(root: Node) -> list[Definition]:
    out: list[Definition] = []
    _rust_items(root, "", True, out)
    return out


def _rust_items(parent: Node, prefix: str, top_level: bool, out: list[Definition]) -> None:
    for item, start in _preambled(parent.named_children, _RUST_PREAMBLE, _RUST_COMMENTS):
        body = item.child_by_field_name("body")
        if item.type == "impl_item":
            if body is not None:
                _rust_items(body, _join(prefix, _rust_type_name(item.child_by_field_name("type"))), False, out)
            continue
        if item.type == "foreign_mod_item":
            if body is not None:
                _rust_items(body, prefix, top_level, out)
            continue
        kind = _RUST_KINDS.get(item.type)
        name = item.child_by_field_name("name")
        if kind is None or name is None:
            continue
        qualname = _join(prefix, _text(name))
        public = any(child.type == "visibility_modifier" for child in item.named_children)
        out.append(Definition(qualname, start, kind, top_level, public))
        if body is None:
            continue
        if item.type == "mod_item":
            _rust_items(body, qualname, top_level, out)
        elif item.type == "trait_item":
            _rust_items(body, qualname, False, out)
        elif body.type in ("field_declaration_list", "enum_variant_list"):
            _rust_fields(body, qualname, out)


def _rust_fields(body: Node, prefix: str, out: list[Definition]) -> None:
    for field, start in _preambled(body.named_children, _RUST_PREAMBLE, _RUST_COMMENTS):
        name = field.child_by_field_name("name")
        if field.type in ("field_declaration", "enum_variant") and name is not None:
            out.append(Definition(_join(prefix, _text(name)), start, VALUE, False, False))


def _rust_type_name(node: Node) -> str:
    if node.type == "generic_type":
        node = node.child_by_field_name("type")
    if node.type == "scoped_type_identifier":
        node = node.child_by_field_name("name")
    return _text(node)


# C and C++

_C_COMMENTS = frozenset({"comment"})
_C_TRANSPARENT = frozenset({"preproc_ifdef", "preproc_if", "preproc_else", "preproc_elif", "preproc_elifdef"})
_C_SPECIFIERS = frozenset({"class_specifier", "struct_specifier", "union_specifier", "enum_specifier"})
_C_NAMES = frozenset(
    {
        "identifier",
        "field_identifier",
        "type_identifier",
        "qualified_identifier",
        "destructor_name",
        "operator_name",
        "template_function",
    }
)


@dataclass(frozen=True)
class _CScope:
    prefix: str
    top_level: bool
    hidden: bool


def _walk_c(root: Node) -> list[Definition]:
    out: list[Definition] = []
    _c_items(root.named_children, _CScope("", True, False), out)
    return out


def _c_items(children: Iterable[Node], scope: _CScope, out: list[Definition]) -> None:
    for item, start in _preambled(children, frozenset(), _C_COMMENTS):
        _c_item(item, start, scope, out)


def _c_item(item: Node, start: int, scope: _CScope, out: list[Definition]) -> None:
    kind = item.type
    if kind in _C_TRANSPARENT:
        _c_items(item.named_children, scope, out)
    elif kind == "template_declaration":
        for child in item.named_children:
            if child.type != "template_parameter_list":
                _c_item(child, start, scope, out)
    elif kind == "linkage_specification":
        body = item.child_by_field_name("body")
        if body is not None and body.type == "declaration_list":
            _c_items(body.named_children, scope, out)
        elif body is not None:
            _c_item(body, start, scope, out)
    elif kind == "namespace_definition":
        _c_namespace(item, start, scope, out)
    elif kind in _C_SPECIFIERS:
        _c_specifier(item, start, scope, None, out)
    elif kind == "function_definition":
        _c_declarator(item, item.child_by_field_name("declarator"), start, scope, out)
    elif kind in ("declaration", "field_declaration", "type_definition"):
        specifier = item.child_by_field_name("type")
        declarators = item.children_by_field_name("declarator")
        if specifier is not None and specifier.type in _C_SPECIFIERS:
            fallback = None
            if kind == "type_definition" and declarators:
                fallback = _c_declared_name(declarators[0])
            _c_specifier(specifier, start, scope, fallback, out)
        for declarator in declarators:
            _c_declarator(item, declarator, start, scope, out, typedef=kind == "type_definition")
    elif kind == "alias_declaration":
        name = _text(item.child_by_field_name("name"))
        out.append(Definition(_join(scope.prefix, name), start, DEFINITION, scope.top_level, not scope.hidden))
    elif kind in ("preproc_def", "preproc_function_def"):
        name = _text(item.child_by_field_name("name"))
        out.append(Definition(_join(scope.prefix, name), start, VALUE, scope.top_level, not scope.hidden))


def _c_namespace(item: Node, start: int, scope: _CScope, out: list[Definition]) -> None:
    body = item.child_by_field_name("body")
    name = item.child_by_field_name("name")
    if name is None:
        inner = _CScope(scope.prefix, scope.top_level, True)
    else:
        prefix = scope.prefix
        for part in _c_name_parts(name):
            prefix = _join(prefix, part)
            out.append(Definition(prefix, start, NAMESPACE, scope.top_level, not scope.hidden))
        inner = _CScope(prefix, scope.top_level, scope.hidden)
    if body is not None:
        _c_items(body.named_children, inner, out)


def _c_specifier(
    specifier: Node, start: int, scope: _CScope, fallback: str | None, out: list[Definition]
) -> None:
    body = specifier.child_by_field_name("body")
    name = specifier.child_by_field_name("name")
    if body is None or (name is None and fallback is None):
        return
    qualname = _join(scope.prefix, ".".join(_c_name_parts(name)) if name is not None else fallback)
    if name is not None:
        out.append(Definition(qualname, start, DEFINITION, scope.top_level, not scope.hidden))
    if body.type == "enumerator_list":
        for enumerator in body.named_children:
            if enumerator.type == "enumerator":
                member = _join(qualname, _text(enumerator.child_by_field_name("name")))
                out.append(Definition(member, _line(enumerator), VALUE, False, False))
    else:
        _c_items(body.named_children, _CScope(qualname, False, scope.hidden), out)


def _c_declarator(
    item: Node, declarator: Node | None, start: int, scope: _CScope, out: list[Definition], typedef: bool = False
) -> None:
    found = _c_unwrap(declarator)
    if found is None:
        return
    name, is_function = found
    parts = _c_name_parts(name)
    is_static = any(
        child.type == "storage_class_specifier" and _text(child) == "static" for child in item.named_children
    )
    kind = DEFINITION if is_function or typedef else VALUE
    out.append(
        Definition(
            _join(scope.prefix, ".".join(parts)),
            start,
            kind,
            scope.top_level and len(parts) == 1,
            not scope.hidden and not is_static,
        )
    )


def _c_unwrap(node: Node | None) -> tuple[Node, bool] | None:
    """Follow nested declarators down to the declared name, noting whether it is a function."""
    is_function = False
    while node is not None:
        if node.type == "function_declarator":
            is_function = True
        if node.type in _C_NAMES:
            return node, is_function
        inner = node.child_by_field_name("declarator")
        if inner is None and node.type in ("reference_declarator", "parenthesized_declarator"):
            inner = node.named_children[-1] if node.named_children else None
        node = inner
    return None


def _c_declared_name(declarator: Node) -> str | None:
    found = _c_unwrap(declarator)
    return ".".join(_c_name_parts(found[0])) if found is not None else None


def _c_name_parts(node: Node) -> list[str]:
    if node.type == "qualified_identifier":
        scope = node.child_by_field_name("scope")
        return (_c_name_parts(scope) if scope is not None else []) + _c_name_parts(node.child_by_field_name("name"))
    if node.type in ("template_type", "template_function"):
        return [_text(node.child_by_field_name("name"))]
    if node.type == "nested_namespace_specifier":
        return [part for child in node.named_children for part in _c_name_parts(child)]
    return [_text(node)]


# Go

_GO_COMMENTS = frozenset({"comment"})


def _walk_go(root: Node) -> list[Definition]:
    out: list[Definition] = []
    for item, start in _preambled(root.named_children, frozenset(), _GO_COMMENTS):
        if item.type == "function_declaration":
            name = _text(item.child_by_field_name("name"))
            out.append(Definition(name, start, DEFINITION, True, name[:1].isupper()))
        elif item.type == "method_declaration":
            name = _text(item.child_by_field_name("name"))
            receiver = _go_receiver_name(item.child_by_field_name("receiver"))
            out.append(Definition(_join(receiver, name), start, DEFINITION, False, name[:1].isupper()))
        elif item.type == "type_declaration":
            for spec in item.named_children:
                if spec.type in ("type_spec", "type_alias"):
                    name = _text(spec.child_by_field_name("name"))
                    out.append(Definition(name, _line(spec), DEFINITION, True, name[:1].isupper()))
        elif item.type in ("const_declaration", "var_declaration"):
            for spec in _go_specs(item):
                for name_node in spec.children_by_field_name("name"):
                    name = _text(name_node)
                    out.append(Definition(name, _line(spec), VALUE, True, name[:1].isupper()))
    return out


def _go_specs(node: Node) -> Iterator[Node]:
    for child in node.named_children:
        if child.type in ("const_spec", "var_spec"):
            yield child
        elif child.type == "var_spec_list":
            yield from _go_specs(child)


def _go_receiver_name(receiver: Node) -> str:
    for parameter in receiver.named_children:
        node = parameter.child_by_field_name("type")
        if node is None:
            continue
        if node.type == "pointer_type":
            node = node.named_children[0]
        if node.type == "generic_type":
            node = node.child_by_field_name("type")
        return _text(node)
    return ""


# Java

_JAVA_COMMENTS = frozenset({"line_comment", "block_comment"})
_JAVA_TYPES = frozenset(
    {
        "class_declaration",
        "interface_declaration",
        "enum_declaration",
        "record_declaration",
        "annotation_type_declaration",
    }
)
_JAVA_METHODS = frozenset(
    {
        "method_declaration",
        "constructor_declaration",
        "compact_constructor_declaration",
        "annotation_type_element_declaration",
    }
)


def _walk_java(root: Node) -> list[Definition]:
    out: list[Definition] = []
    _java_members(root.named_children, "", True, out)
    return out


def _java_members(children: Iterable[Node], prefix: str, top_level: bool, out: list[Definition]) -> None:
    for item, start in _preambled(children, frozenset(), _JAVA_COMMENTS):
        if item.type in _JAVA_TYPES or item.type in _JAVA_METHODS:
            name = item.child_by_field_name("name")
            if name is None:
                continue
            qualname = _join(prefix, _text(name))
            out.append(Definition(qualname, start, DEFINITION, top_level, _java_public(item)))
            body = item.child_by_field_name("body")
            if item.type in _JAVA_TYPES and body is not None:
                _java_members(body.named_children, qualname, False, out)
        elif item.type in ("field_declaration", "constant_declaration"):
            for declarator in item.children_by_field_name("declarator"):
                name = _text(declarator.child_by_field_name("name"))
                out.append(Definition(_join(prefix, name), start, VALUE, top_level, _java_public(item)))
        elif item.type == "enum_constant":
            name = _text(item.child_by_field_name("name"))
            out.append(Definition(_join(prefix, name), start, VALUE, False, True))
        elif item.type == "enum_body_declarations":
            _java_members(item.named_children, prefix, top_level, out)


def _java_public(item: Node) -> bool:
    modifiers = next((child for child in item.named_children if child.type == "modifiers"), None)
    return modifiers is not None and any(child.type == "public" for child in modifiers.children)


# @doc: docs/VerificationTools.md#71-언어-모듈
LANGUAGES = {
    "python": Language("python", _PY_COMMENTS, tree_sitter_python.language, _walk_python, _python_docstring),
    "javascript": Language("javascript", _JS_COMMENTS, tree_sitter_javascript.language, _walk_js),
    "typescript": Language("typescript", _JS_COMMENTS, tree_sitter_typescript.language_typescript, _walk_js),
    "tsx": Language("tsx", _JS_COMMENTS, tree_sitter_typescript.language_tsx, _walk_js),
    "rust": Language("rust", _RUST_COMMENTS, tree_sitter_rust.language, _walk_rust),
    "c": Language("c", _C_COMMENTS, tree_sitter_c.language, _walk_c),
    "cpp": Language("cpp", _C_COMMENTS, tree_sitter_cpp.language, _walk_c),
    "go": Language("go", _GO_COMMENTS, tree_sitter_go.language, _walk_go),
    "java": Language("java", _JAVA_COMMENTS, tree_sitter_java.language, _walk_java),
}
