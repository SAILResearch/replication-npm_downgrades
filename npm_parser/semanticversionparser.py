from parsimonious.grammar import Grammar
from parsimonious import NodeVisitor
from kids.cache import cache


class VersionParser(object):
    def parse(self, version_str):
        print(version_str)


class RelaxedSemanticVersionParser(VersionParser):
    grammar = Grammar(r"""
        semantic_version = major ("." minor ("." patch)) (~"[\-\.]"? pre_release)* (~"[\-\.\+]"? build)*
        major            = nr ""
        minor            = nr ""
        patch            = nr ""
        nr               = "0" / (~"[1-9]" (~"[0-9]")*)
        text             = ~"[a-zA-Z]"*
        pre_release      = pre_qualifier? ~"[\.\-]"? pre_nr?
        pre_qualifier    = text ""
        pre_nr           = nr ""
        build            = build_qualifier? ~"[\.\-]"? build_nr?
        build_nr         = nr ""
        build_qualifier  = text ""
        """)

    @classmethod
    @cache
    def parse(cls, version_str):
        tree = cls.grammar.parse(version_str)

        vv = VersionVisitor()
        semantic_version = vv.get_semver(tree)

        return semantic_version


class SemanticVersionParser(VersionParser):
    grammar = Grammar(r"""
        semantic_version = major ("." minor ("." patch)) ("-" pre_release)? ("+" build)?
        major            = nr ""
        minor            = nr ""
        patch            = nr ""
        nr               = "0" / (~"[1-9]" (~"[0-9]")*)
        text             = ~"[a-zA-Z]"+
        pre_release      = pre_qualifier? ("."? pre_nr)?
        pre_qualifier    = text ""
        pre_nr           = nr ""
        build            = build_qualifier? ("."? build_nr)?
        build_nr         = nr ""
        build_qualifier  = text ""     
        """)

    @classmethod
    @cache
    def parse(cls, version_str):
        tree = cls.grammar.parse(version_str)

        vv = VersionVisitor()
        semantic_version = vv.get_semver(tree)

        return semantic_version


class VersionVisitor(NodeVisitor):
    def __init__(self):
        self.semantic_version = None
        self.major = None
        self.minor = None
        self.patch = None
        self.pre_release = None
        self.pre_qualifier = None
        self.pre_nr = None
        self.build = None
        self.build_nr = None
        self.build_qualifier = None

        self.semver = None

    def get_semver(self, tree):
        self.visit(tree)

        return self.semver

    def visit_semantic_version(self, node, children):
        if self.semantic_version != node.text:
            self.semantic_version = node.text

            self.semver = {"major": self.major, "minor": self.minor, "patch": self.patch, \
                            "pre_release": self.pre_release, "pre_qualifier": self.pre_qualifier, "pre_nr": self.pre_nr, \
                            "build": self.build, "build_qualifier": self.build_qualifier, "build_nr": self.build_nr}
            
    def visit_major(self, node, children):
        if self.major != node.text:
            self.major = node.text

    def visit_minor(self, node, children):
        if self.minor != node.text:
            self.minor = node.text

    def visit_patch(self, node, children):
        if self.patch != node.text:
            self.patch = node.text

    def visit_pre_release(self, node, children):
        if self.pre_release != node.text:
            self.pre_release = node.text

    def visit_pre_qualifier(self, node, children):
        if self.pre_qualifier != node.text:
            self.pre_qualifier = node.text

    def visit_pre_nr(self, node, children):
        if self.pre_nr != node.text:
            self.pre_nr = node.text

    def visit_build(self, node, children):
        if self.build != node.text:
            self.build = node.text

    def visit_build_nr(self, node, children):
        if self.build_nr != node.text:
            self.build_nr = node.text

    def visit_build_qualifier(self, node, children):
        if self.build_qualifier != node.text:
            self.build_qualifier = node.text

    def generic_visit(self, node, visited_children):
        return node


if __name__ == "__main__":
    parser = RelaxedSemanticVersionParser()

    print(parser.parse("1.0.0"))
    print(parser.parse("1.0.0-alpha.5.9.4"))
    print(parser.parse("1.0.0-alpha.5.9.4+build.1.5"))
    print(parser.parse("1.0.0-alpha10"))
    print(parser.parse("1.0.0-alpha10-build18"))
    print(parser.parse("1.0.0-alpha-10-15-20"))
    print(parser.parse("1.0.0-alpha-10-15-20+build.1.2.3"))
    print(parser.parse("1.0.0"))
    print(parser.parse("1.0.0-alpha10"))
    print(parser.parse("1.0.0-alpha.10.2.1"))
    print(parser.parse("1.0.0-alpha+build10"))
    print(parser.parse("1.0.0-alpha-10-15-20+build1.2.3"))

    parser = SemanticVersionParser()

    print(parser.parse("1.0.0"))
    print(parser.parse("1.0.0-alpha.5"))
    print(parser.parse("1.0.0-alpha.5+build.1"))
    print(parser.parse("1.0.0-alpha10"))
    print(parser.parse("1.0.0-alpha50+build10"))
    print(parser.parse("1.0.0-alpha"))
    print(parser.parse("1.0.0-alpha+build"))
