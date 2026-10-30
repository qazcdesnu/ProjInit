"""Tests for the per-language symbol rules.

@doc: docs/VerificationTools.md#5-테스트
"""

import unittest

from projinit.doclib import LANGUAGE_SUFFIXES
from projinit.languages import DEFINITION, LANGUAGES, NAMESPACE, VALUE, parse

_PYTHON = '''"""Module."""
LIMIT = 3
_hidden: int = 1
a = b = 2


@decorator
def run():
    def inner():
        local = 1


class _Thing:
    size = 0

    async def go(self):
        pass
'''

_TYPESCRIPT = """@dec
export class A {
  @d m() {}
  x: number = 1;
}
export const k = () => 1;
const plain = 1;
namespace N { export function g() {} }
declare module 'm' { function h(): void; }
interface I { p: string; q(): void }
enum E { A, B = 2 }
abstract class Z { abstract z(): void }
"""

_RUST = """#![allow(x)]
#[derive(X)]
pub struct S { pub a: i32 }
impl<T> Tr for Vec<T> { fn f() {} }
impl a::B { const K: i32 = 1; }
mod m { pub fn g() {} }
extern "C" { fn c(); }
macro_rules! mm { () => {} }
trait T { fn t(&self); type X; }
enum E { A, B(i32) }
"""

_C = """#ifndef X
#define X
struct S { int x; };
typedef struct { int y; } T;
static int f(void);
int *g(int a) { return 0; }
enum E { A };
int counter;
#endif
"""

_CPP = """namespace a::b {
template<typename T> class C : public B {
 public:
  C();
  ~C();
  int m() const;
  int v;
  struct In {};
};
}
namespace { void p() {} }
template<typename T> int a::b::C<T>::m() const { return 0; }
extern "C" { int q(); }
using X = int;
int& r();
bool operator==(const S&, const S&);
"""

_GO = """package p

func F() {}
func (r *Recv[T]) M() {}
type A struct{ x int }
type B = int
var v = 1
const c = 1
"""

_JAVA = """package p;
@Ann
public class A {
  public A() {}
  private int x, y;
  void m() {}
  enum E { P, Q; void e() {} }
  interface I { int K = 1; void i(); }
  record R(int a) {}
}
class Hidden {}
"""


def _definitions(language: str, source: str) -> dict[str, tuple[str, bool, bool, int]]:
    lang = LANGUAGES[language]
    found = {}
    for definition in lang.walk(parse(lang, source.encode()).root_node):
        found.setdefault(
            definition.qualname, (definition.kind, definition.top_level, definition.public, definition.line)
        )
    return found


class LanguagesTest(unittest.TestCase):
    """@doc: docs/VerificationTools.md#5-테스트"""

    def assert_symbols(self, found: dict, expected: dict) -> None:
        for qualname, (kind, top_level, public) in expected.items():
            self.assertIn(qualname, found)
            self.assertEqual(found[qualname][:3], (kind, top_level, public), qualname)

    def test_every_suffix_has_a_language(self) -> None:
        self.assertEqual(set(LANGUAGE_SUFFIXES.values()), set(LANGUAGES))

    def test_python(self) -> None:
        found = _definitions("python", _PYTHON)
        self.assert_symbols(
            found,
            {
                "LIMIT": (VALUE, True, True),
                "_hidden": (VALUE, True, False),
                "a": (VALUE, True, True),
                "b": (VALUE, True, True),
                "run": (DEFINITION, True, True),
                "run.inner": (DEFINITION, False, True),
                "_Thing": (DEFINITION, True, False),
                "_Thing.size": (VALUE, False, True),
                "_Thing.go": (DEFINITION, False, True),
            },
        )
        self.assertNotIn("run.inner.local", found)
        self.assertEqual(found["run"][3], 7)

    def test_python_docstring(self) -> None:
        lang = LANGUAGES["python"]
        tree = parse(lang, b'"""Top.\n\n@doc: x\n"""\n')
        self.assertEqual(lang.module_docstring(tree.root_node), (1, "Top.\n\n@doc: x\n"))

    def test_typescript(self) -> None:
        found = _definitions("typescript", _TYPESCRIPT)
        self.assert_symbols(
            found,
            {
                "A": (DEFINITION, True, True),
                "A.m": (DEFINITION, False, False),
                "A.x": (VALUE, False, False),
                "k": (DEFINITION, True, True),
                "plain": (VALUE, True, False),
                "N": (NAMESPACE, True, False),
                "N.g": (DEFINITION, True, True),
                "m": (NAMESPACE, True, False),
                "m.h": (DEFINITION, True, False),
                "I": (DEFINITION, True, False),
                "I.p": (VALUE, False, False),
                "I.q": (DEFINITION, False, False),
                "E.A": (VALUE, False, False),
                "E.B": (VALUE, False, False),
                "Z.z": (DEFINITION, False, False),
            },
        )
        self.assertEqual(found["A"][3], 1)
        self.assertEqual(found["A.m"][3], 3)

    def test_javascript_and_tsx(self) -> None:
        found = _definitions("javascript", "class A { #p = 1; static s() {} }\nexport const f = function () {};\n")
        self.assert_symbols(
            found, {"A": (DEFINITION, True, False), "A.#p": (VALUE, False, False), "f": (DEFINITION, True, True)}
        )
        found = _definitions("tsx", "export const View = () => <div />;\n")
        self.assert_symbols(found, {"View": (DEFINITION, True, True)})

    def test_rust(self) -> None:
        found = _definitions("rust", _RUST)
        self.assert_symbols(
            found,
            {
                "S": (DEFINITION, True, True),
                "S.a": (VALUE, False, False),
                "Vec.f": (DEFINITION, False, False),
                "B.K": (VALUE, False, False),
                "m": (NAMESPACE, True, False),
                "m.g": (DEFINITION, True, True),
                "c": (DEFINITION, True, False),
                "mm": (DEFINITION, True, False),
                "T": (DEFINITION, True, False),
                "T.t": (DEFINITION, False, False),
                "T.X": (VALUE, False, False),
                "E.A": (VALUE, False, False),
            },
        )
        self.assertEqual(found["S"][3], 2)

    def test_c(self) -> None:
        found = _definitions("c", _C)
        self.assert_symbols(
            found,
            {
                "X": (VALUE, True, True),
                "S": (DEFINITION, True, True),
                "S.x": (VALUE, False, True),
                "T": (DEFINITION, True, True),
                "T.y": (VALUE, False, True),
                "f": (DEFINITION, True, False),
                "g": (DEFINITION, True, True),
                "E": (DEFINITION, True, True),
                "E.A": (VALUE, False, False),
                "counter": (VALUE, True, True),
            },
        )

    def test_cpp(self) -> None:
        found = _definitions("cpp", _CPP)
        self.assert_symbols(
            found,
            {
                "a": (NAMESPACE, True, True),
                "a.b": (NAMESPACE, True, True),
                "a.b.C": (DEFINITION, True, True),
                "a.b.C.C": (DEFINITION, False, True),
                "a.b.C.~C": (DEFINITION, False, True),
                "a.b.C.m": (DEFINITION, False, True),
                "a.b.C.v": (VALUE, False, True),
                "a.b.C.In": (DEFINITION, False, True),
                "p": (DEFINITION, True, False),
                "q": (DEFINITION, True, True),
                "X": (DEFINITION, True, True),
                "r": (DEFINITION, True, True),
                "operator==": (DEFINITION, True, True),
            },
        )
        self.assertEqual(found["a.b.C"][3], 2)

    def test_go(self) -> None:
        found = _definitions("go", _GO)
        self.assert_symbols(
            found,
            {
                "F": (DEFINITION, True, True),
                "Recv.M": (DEFINITION, False, True),
                "A": (DEFINITION, True, True),
                "B": (DEFINITION, True, True),
                "v": (VALUE, True, False),
                "c": (VALUE, True, False),
            },
        )

    def test_java(self) -> None:
        found = _definitions("java", _JAVA)
        self.assert_symbols(
            found,
            {
                "A": (DEFINITION, True, True),
                "A.A": (DEFINITION, False, True),
                "A.x": (VALUE, False, False),
                "A.y": (VALUE, False, False),
                "A.m": (DEFINITION, False, False),
                "A.E.P": (VALUE, False, True),
                "A.E.e": (DEFINITION, False, False),
                "A.I.K": (VALUE, False, False),
                "A.I.i": (DEFINITION, False, False),
                "A.R": (DEFINITION, False, False),
                "Hidden": (DEFINITION, True, False),
            },
        )
        self.assertEqual(found["A"][3], 2)


if __name__ == "__main__":
    unittest.main()
