from semanticversionparser import SemanticVersionParser, RelaxedSemanticVersionParser

class Version():
    pass

class SemanticVersion(Version):
    major = None
    minor = None
    patch = None
    pre_release = None
    build = None

    def __init__(self, version_str):
        semantic_version = SemanticVersionParser().parse(version_str)

        self.major = semantic_version["major"]
        self.minor = semantic_version["minor"]
        self.patch = semantic_version["patch"]
        self.pre_release = semantic_version["pre_release"]
        self.build = semantic_version["build"]

    def __str__(self):
        if self.build != None:
            if self.pre_release != None:
                return "{}.{}.{}-{}+{}".format(self.major, self.minor, self.patch, self.pre_release, self.build)
            else:
                return "{}.{}.{}+{}".format(self.major, self.minor, self.patch, self.build)
        elif self.pre_release != None:
            return "{}.{}.{}-{}".format(self.major, self.minor, self.patch, self.pre_release)
        elif self.major != None and self.minor != None and self.patch != None:
            return "{}.{}.{}".format(self.major, self.minor, self.patch)
        else:
            raise ValueError("{} doesn't match Semantic Version 2.0".format(self))

class RelaxedSemanticVersion(Version):
    major = "0"
    minor = "0"
    patch = "0"
    pre_release = None
    build = None

    def __init__(self, major, minor, patch, pre_release=None, build=None):
        self.major = str(major)
        self.minor = str(minor)
        self.patch = str(patch)
        self.pre_release = str(pre_release)
        self.build = str(build)

    def parse(self, version_str):
        semantic_version = RelaxedSemanticVersionParser().parse(version_str)
        self.major = semantic_version["major"]
        self.minor = semantic_version["minor"]
        self.patch = semantic_version["patch"]
        self.pre_release = semantic_version["pre_release"]
        self.build = semantic_version["build"]

    def __str__(self):
        if self.build != None:
            if self.pre_release != None:
                return "{}.{}.{}-{}+{}".format(self.major, self.minor, self.patch, self.pre_release, self.build)
            else:
                return "{}.{}.{}+{}".format(self.major, self.minor, self.patch, self.build)
        elif self.pre_release != None:
            return "{}.{}.{}-{}".format(self.major, self.minor, self.patch, self.pre_release)
        else:
            return "{}.{}.{}".format(self.major, self.minor, self.patch)