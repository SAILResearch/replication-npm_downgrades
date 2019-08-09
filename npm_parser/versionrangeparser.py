import time

from parsimonious.grammar import Grammar
from parsimonious import NodeVisitor, ParseError

from semanticversionrange import SemanticVersionComparator, SemanticVersionRange

class VersionRangeParser(object):
    def parse(self, version_range_str):
        print(version_range_str)

class NodeVersionRangeParser(VersionRangeParser):
    grammar = Grammar(r"""
        range_set   = range (logical_or range)*
        logical_or  = " "* "||" " "*
        range       = hyphen / (simple (" " simple)*) / ""
        hyphen      = hpart1 " - " hpart2
        hpart1      = ver_num1 qualifier1?
        hpart2      = ver_num2 qualifier2?
        simple      = primitive / partial
        primitive   = operator " "* partial
        operator    = ">=" / "<=" / "=" / "<" / ">" / "~" / "^"
        partial     = "v"? ver_num qualifier?
        ver_num1    = ver_num ""
        ver_num2    = ver_num ""
        ver_num     = xr ("." xr ("." xr)?)?   
        xr          = "x" / "X" / "*" / "latest" / nr / ~"^$"
        nr          = "0" / (~"[1-9]" (~"[0-9]")*)
        qualifier   = ("-" pre)* ("+" build )*
        qualifier1  = ("-" pre1)* ("+" build1 )*
        qualifier2  = ("-" pre2)* ("+" build2 )*
        pre         = parts ""
        pre1        = parts ""
        pre2        = parts ""
        build       = parts ""
        build1      = parts ""
        build2      = parts ""
        parts       = part ("." part)*
        part        = nr / ~"[a-z0-9]"+
        """)

    def parse(self, version_range_str):
        tree = self.grammar.parse(version_range_str)

        vv = NodeVersionRangeVisitor()
        simples, hyphens = vv.get_simples_and_hyphens(tree)

        svr = SemanticVersionRange()
        for s in simples:
            svc = SemanticVersionComparator(s)
            svr.addComparatorToRange(svc)

        for h in hyphens:
            svc = SemanticVersionComparator(h)
            svr.addComparatorToRange(svc)

        return svr

class NodeVersionRangeVisitor(NodeVisitor):
    def __init__(self):
        self.partial = None
        self.operator = None
        self.simple = None
        self.range = None
        self.hyphen = None
        self.pre = None
        self.pre1 = None
        self.pre2 = None
        self.build = None
        self.build1 = None
        self.build2 = None
        self.ver_num = None
        self.ver_num1 = None
        self.ver_num2 = None
        self.hpart1 = None
        self.hpart2 = None
        self.logical_or = 0

        self.simples = []
        self.hyphens = []

    def get_simples_and_hyphens(self, tree):
        self.visit(tree)

        return self.simples, self.hyphens

    def visit_hpart1(self, node, children):
        if self.hpart1 != node.text:
            self.hpart1 = node.text

    def visit_hpart2(self, node, children):
        if self.hpart2 != node.text:
            self.hpart2 = node.text

    def visit_ver_num(self, node, children):
        if self.ver_num != node.text:
            self.ver_num = node.text

    def visit_ver_num1(self, node, children):
        if self.ver_num1 != node.text:
            self.ver_num1 = node.text

    def visit_ver_num2(self, node, children):
        if self.ver_num2 != node.text:
            self.ver_num2 = node.text

    def visit_pre(self, node, children):
        if self.pre != node.text:
            self.pre = node.text

    def visit_pre1(self, node, children):
        if self.pre1 != node.text:
            self.pre1 = node.text

    def visit_pre2(self, node, children):
        if self.pre2 != node.text:
            self.pre2 = node.text

    def visit_build(self, node, children):
        if self.build != node.text:
            self.build = node.text

    def visit_build1(self, node, children):
        if self.build1 != node.text:
            self.build1 = node.text

    def visit_build2(self, node, children):
        if self.build2 != node.text:
            self.build2 = node.text

    def visit_partial(self, node, children):
        if self.partial != node.text:
            self.partial = node.text

    def visit_operator(self, node, children):
        if self.operator != node.text:
            self.operator = node.text

    def visit_logical_or(self, node, children):
        if self.operator != node.text:
            self.logical_or = self.logical_or + 1

    def visit_range(self, node, children):
        if self.range != node.text:
            self.range = node.text

    def visit_simple(self, node, children):
        if self.simple != node.text:
            self.simple = node.text

            self.simples.append({"simple": self.simple, "operator": self.operator, "logical_or": self.logical_or, \
                                 "ver_num": self.ver_num, "pre": self.pre, "build": self.build})

    def visit_hyphen(self, node, children):
        if self.hyphen != node.text:
            self.hyphen = node.text

            self.hyphens.append({"hyphen": self.hyphen, "part1": self.hpart1, "part2": self.hpart2, \
                                 "ver_num1": self.ver_num1, "ver_num2": self.ver_num2, "pre1": self.pre1, \
                                 "pre2": self.pre2, "build1": self.build1, "build2": self.build2, \
                                 "logical_or": self.logical_or})

    def visit_partial1(self, node, children):
        if self.partial1 != node.text:
            self.partial1= node.text

    def visit_partial2(self, node, children):
        if self.partial2 != node.text:
            self.partial2= node.text

    def generic_visit(self, node, visited_children):
        return node


if __name__ == "__main__":
    nvrp = NodeVersionRangeParser()
    #print(nvrp.parse("1.0.4 - 2.x || ~2.2 || >= 3.2.9-alpha.4 <4.0.0-beta.5+build.7"))
    #print("")

    print(nvrp.parse("v2.1.0-beta.22-other+build"))
    print(nvrp.parse("^2.1.0-beta.22"))
    print(nvrp.parse("~v2.1.0-beta.22"))

    print(nvrp.parse(""))
    print(nvrp.parse("1"))
    print("")


    print(nvrp.parse("2.1.x"))
    print("")
    print(nvrp.parse("^1.2.3"))
    print("")
    print(nvrp.parse("^0.2.3"))
    print("")
    print(nvrp.parse("^0.0.3"))
    print("")
    print(nvrp.parse("^1.2.34-beta.2"))
    print("")
    print(nvrp.parse("^1.22.x"))
    print("")
    print(nvrp.parse("^0.0.x"))
    print("")
    print(nvrp.parse("^0.0"))
    print("")
    print(nvrp.parse("^1.x"))
    print("")
    print(nvrp.parse("^0.x"))
    print("")
    print(nvrp.parse("~1.2.3"))
    print("")
    print(nvrp.parse("~1.2"))
    print("")
    print(nvrp.parse("~1"))
    print("")
    print(nvrp.parse("~0.2.3"))
    print("")
    print(nvrp.parse("~0.23"))
    print("")
    print(nvrp.parse("~0"))
    print("")
    print(nvrp.parse("~0.x"))
    print("")
    print(nvrp.parse("*"))
    print("")
    print(nvrp.parse('>=10.0.0   ||   <2.3.x'))
    print("")
    print(nvrp.parse('1.2.3 - 2.3.4'))
    print("")
    print(nvrp.parse('1.2 - 2.3.4'))
    print("")
    print(nvrp.parse('1.2.3 - 2.3'))
    print("")
    print(nvrp.parse('1.2.3 - 2'))
    print("")
    print(nvrp.parse('1.2.3'))
    print("")
    print(nvrp.parse('1.0.4 - 2.x'))
    print("")
    print(nvrp.parse('~2.0'))
    print("")
    print(nvrp.parse('^2.0'))
    print("")
    print(nvrp.parse('>2.0'))
    print("")
    print(nvrp.parse('<2'))
    print("")
    print(nvrp.parse('>=2.3.4'))
    print("")
    print(nvrp.parse('>=2.3-rc2+build3'))
    print("")
    print(nvrp.parse('0.0.3'))
    print("")
    print(nvrp.parse('10.x.0'))
    print("")

    begin = time.time()
    r = 10000
    for i in range(1000):
        nvrp.parse("1.0.4 - 2.x || ~2.2 || >= 3.2.9-alpha.4 <4.0.0-beta.5+build.7")
        nvrp.parse("1")
        nvrp.parse("2.1.x")
        nvrp.parse("^1.2.3")
        nvrp.parse("^0.2.3")
        nvrp.parse("^0.0.3")
        nvrp.parse("^1.2.3-beta.2")
        nvrp.parse("^1.2.x")
        nvrp.parse("^0.0.x")
        nvrp.parse("^0.0")
        nvrp.parse("^1.x")
        nvrp.parse("^0.x")
        nvrp.parse("~1.2.3")
        nvrp.parse("~1.2")
        nvrp.parse("~1")
        nvrp.parse("~0.2.3")
        nvrp.parse("~0.2")
        nvrp.parse("~0")
        nvrp.parse("~0.x")
        nvrp.parse("*")
        nvrp.parse('>=1.0.0   ||   <2.3.x')
        nvrp.parse('1.2.3 - 2.3.4')
        nvrp.parse('1.2 - 2.3.4')
        nvrp.parse('1.2.3 - 2.3')
        nvrp.parse('1.2.3 - 2')
    end = time.time()
    print("parsed 25 different version ranges {} times in {} seconds".format(r, (end - begin)))
    exit(0)
