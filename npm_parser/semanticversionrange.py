from semanticversionparser import SemanticVersionParser

import time

class SemanticVersionRange(set):
    wildcards = ('x', 'X', '*', 'latest', '')
    svp = SemanticVersionParser()

    def addComparatorToRange(self, comparator):
        try:
            comp1, comp2 = SemanticVersionComparatorFacade().simpleComparators(comparator)

            self.add(comp1)
            self.add(comp2)
        except KeyError:
            try:
                comp1, comp2 = SemanticVersionComparatorFacade().hyphenComparators(comparator)

                self.add(comp1)
                self.add(comp2)
            except KeyError as ke:
                raise KeyError("bad comparator format, cannot add comparator '{}' to range '{}'".format(str(comparator),
                                                                                                        str(self)))\

    def cmp_version(self, version1, comparator):
        operator, version, pre_release, build, raw_string = comparator.unpack()

        version2 = self.svp.parse(version)

        if version1['major'] > version2['major']:
            return 1
        elif version1['major'] < version2['major']:
            return -1

        if version1['minor'] > version2['minor']:
            return 1
        elif version1['minor'] < version2['minor']:
            return -1

        if version1['patch'] > version2['patch']:
            return 1
        elif version1['patch'] < version2['patch']:
            return -1

        return 0

class SemanticVersionComparatorFacade():
    wildcards = ('x', 'X', '*', 'latest', '')

    def __unpackWildcards(self, version, pre, build, logical_or, raw_string):
        major, minor, patch = self.__becomeWildcardVersion(version)

        if major in self.wildcards:
            major, minor, patch = 0, 0, 0

            v1 = "{}.{}.{}".format(major, minor, patch)

            comp1 = SemanticVersionComparator(
                {"operator": ">=", "version": v1, "pre_release": pre, "build": build,
                 "logical_or": logical_or, "raw_string": raw_string})

            return comp1, comp1
        elif minor in self.wildcards:
            minor, patch = 0, 0

            v1 = "{}.{}.{}".format(major, minor, patch)

            major = int(major) + 1
            major = str(major)

            v2 = "{}.{}.{}".format(major, minor, patch)

            comp1 = SemanticVersionComparator(
                {"operator": ">=", "version": v1, "pre_release": pre, "build": build,
                 "logical_or": logical_or, "raw_string": raw_string})
            comp2 = SemanticVersionComparator(
                {"operator": "<", "version": v2, "pre_release": pre, "build": build,
                 "logical_or": logical_or, "raw_string": raw_string})

            return comp1, comp2
        elif patch in self.wildcards:
            patch = 0

            v1 = "{}.{}.{}".format(major, minor, patch)

            minor = int(minor) + 1
            minor = str(minor)

            v2 = "{}.{}.{}".format(major, minor, patch)

            comp1 = SemanticVersionComparator(
                {"operator": ">=", "version": v1, "pre_release": pre, "build": build,
                 "logical_or": logical_or, "raw_string": raw_string})
            comp2 = SemanticVersionComparator(
                {"operator": "<", "version": v2, "pre_release": pre, "build": build,
                 "logical_or": logical_or, "raw_string": raw_string})

            return comp1, comp2
        else:
            raise ValueError("no wildcards to unpack on string '{}'".format(raw_string))

    def __unpackTilde(self, version, pre, build, logical_or, raw_string):
        # version can be splited with "." ?
        major, minor, patch = self.__becomeWildcardVersion(version)

        if major in self.wildcards:
            v1 = "{}.{}.{}".format(0, 0, 0)

            comp1 = SemanticVersionComparator(
                {"operator": ">=", "version": v1, "pre_release": pre, "build": build,
                 "logical_or": logical_or, "raw_string": raw_string})

            return comp1, comp1

        elif minor in self.wildcards:
            v1 = "{}.{}.{}".format(major, 0, 0)

            if int(major) > 0:
                m = int(major) + 1
                m = str(m)

                v2 = "{}.{}.{}".format(m, 0, 0)
            else:
                v2 = "{}.{}.{}".format(1, 0, 0)
        elif patch in self.wildcards:
            v1 = "{}.{}.{}".format(major, minor, 0)

            m = int(minor) + 1
            m = str(m)

            v2 = "{}.{}.{}".format(major, m, 0)
        else:
            v1 = "{}.{}.{}".format(major, minor, patch)

            m = int(minor) + 1
            m = str(m)

            v2 = "{}.{}.{}".format(major, m, 0)

        comp1 = SemanticVersionComparator(
            {"operator": ">=", "version": v1, "pre_release": pre, "build": build,
             "logical_or": logical_or, "raw_string": raw_string})
        comp2 = SemanticVersionComparator(
            {"operator": "<", "version": v2, "pre_release": pre, "build": build,
             "logical_or": logical_or, "raw_string": raw_string})

        return comp1, comp2

    def __becomeWildcardVersion(self, version):
        try:
            # can version be splited with 3 "." ?
            major, minor, patch = version.split(".")

            if major in self.wildcards:
                minor, patch = ("x", "x")
            elif minor in self.wildcards:
                patch = "x"
        except ValueError:
            # if v1 cannot be splited with 2 "."
            patch = "x"
            try:
                major, minor = version.split(".")

                if major in self.wildcards:
                    minor = "x"
            except ValueError:
                # if version cannot be splited with 1 "."
                minor = "x"
                major = version

        return major, minor, patch

    def hyphenComparators(self, comparator):
        try:
            comparator["hyphen"]
            v1 = comparator["part1"]
            v2 = comparator["part2"]

            try:
                comp1, comp2_trash = self.__unpackWildcards(v1, "", "", comparator["logical_or"], comparator["hyphen"])
            except ValueError:
                comp1 = None

            comp2 = None

            v2_operator = "<="
            try:
                major, minor, patch = v2.split(".")
            except ValueError:
                # if v1 cannot be splited with 2 "."
                patch = 0
                v2_operator = "<"

                try:
                    major, minor = v2.split(".")
                    try:
                        minor = int(minor) + 1
                        minor = str(minor)
                    except ValueError as ve:
                        try:
                            comp1_trash, comp2 = self.__unpackWildcards(v2, "", "", comparator["logical_or"], comparator["hyphen"])
                        except:
                            raise ve
                except ValueError:
                    minor = 0
                    major = v2
                    v2_operator = "<"

                    try:
                        major = int(major) + 1
                        major = str(major)
                    except ValueError as ve:
                        try:
                            comp1_trash, comp2 = self.__unpackWildcards(v2, "", "", comparator["logical_or"], comparator["hyphen"])
                        except:
                            raise ve

            v2 = "{}.{}.{}".format(major, minor, patch)

            if comp1 is None:
                comp1 = SemanticVersionComparator(
                    {"operator": ">=", "version": comparator['ver_num1'], "pre_release": comparator['pre1'],
                     "build": comparator['build1'], "logical_or": comparator["logical_or"],
                     "raw_string": comparator["part1"]})
            if comp2 is None:
                comp2 = SemanticVersionComparator(
                    {"operator": v2_operator, "version": comparator['ver_num2'], "pre_release": comparator['pre2'],
                     "build": comparator['build2'], "logical_or": comparator["logical_or"],
                     "raw_string": comparator["part2"]})

            return comp1, comp2
        except KeyError:
            raise KeyError(
                "bad comparator format, must be a dictionary with fields 'hyphen', 'part1' and 'part2', but found {}:'{}'".format(
                    type(comparator), str(comparator)))

    def __unpackExact(self, version, pre, build, logical_or, raw_string):
        # version can be splited with "." ?
        major, minor, patch = self.__becomeWildcardVersion(version)

        if major in self.wildcards:
            v1 = "{}.{}.{}".format(0, 0, 0)

            comp1 = SemanticVersionComparator(
                {"operator": ">=", "version": v1, "pre_release": pre, "build": build,
                 "logical_or": logical_or, "raw_string": raw_string})

            return comp1, comp1

        elif minor in self.wildcards:
            v1 = "{}.{}.{}".format(major, 0, 0)
            v2 = "{}.{}.{}".format(str(int(major) + 1), 0, 0)

            comp1 = SemanticVersionComparator(
                {"operator": ">=", "version": v1, "pre_release": pre, "build": build,
                 "logical_or": logical_or, "raw_string": raw_string})

            comp2 = SemanticVersionComparator(
                {"operator": "<", "version": v2, "pre_release": pre, "build": build,
                 "logical_or": logical_or, "raw_string": raw_string})

            return comp1, comp2

        elif patch in self.wildcards:
            v1 = "{}.{}.{}".format(major, minor, 0)
            v2 = "{}.{}.{}".format(major, str(int(minor) + 1), 0)

            comp1 = SemanticVersionComparator(
                {"operator": ">=", "version": v1, "pre_release": pre, "build": build,
                 "logical_or": logical_or, "raw_string": raw_string})

            comp2 = SemanticVersionComparator(
                {"operator": "<", "version": v2, "pre_release": pre, "build": build,
                 "logical_or": logical_or, "raw_string": raw_string})

            return comp1, comp2

        else:
            v1 = "{}.{}.{}".format(major, minor, patch)

            comp1 = SemanticVersionComparator(
                {"operator": "==", "version": v1, "pre_release": pre, "build": build,
                 "logical_or": logical_or, "raw_string": raw_string})

            return comp1, comp1

    def __unpackCaret(self, version, pre, build, logical_or, raw_string):
        # version can be splited with "." ?
        major, minor, patch = self.__becomeWildcardVersion(version)

        if major in self.wildcards:
            v1 = "{}.{}.{}".format(0, 0, 0)

            comp1 = SemanticVersionComparator( \
                {"operator": ">=", "version": v1, "pre_release": pre, "build": build,
                 "logical_or": logical_or, "raw_string": raw_string})

            return comp1, comp1

        elif minor in self.wildcards:
            v1 = "{}.{}.{}".format(major, 0, 0)

            if int(major) > 0:
                m = int(major) + 1
                m = str(m)

                v2 = "{}.{}.{}".format(m, 0, 0)
            else:
                v2 = "{}.{}.{}".format(1, 0, 0)

        elif patch in self.wildcards:
            v1 = "{}.{}.{}".format(major, minor, 0)

            if int(major) > 0:
                m = int(major) + 1
                m = str(m)

                v2 = "{}.{}.{}".format(m, 0, 0)
            else:
                if int(minor) > 0:
                    m = int(minor) + 1
                    m = str(m)

                    v2 = "{}.{}.{}".format(0, m, 0)
                else:
                    v2 = "{}.{}.{}".format(0, 1, 0)

        else:
            v1 = "{}.{}.{}".format(major, minor, patch)

            if int(major) > 0:
                m = int(major) + 1
                m = str(m)

                v2 = "{}.{}.{}".format(m, 0, 0)
            else:
                if int(minor) > 0:
                    m = int(minor) + 1
                    m = str(m)

                    v2 = "{}.{}.{}".format(0, m, 0)
                else:
                    if int(patch) > 0:

                        m = int(patch) + 1
                        m = str(m)

                        v2 = "{}.{}.{}".format(0, 0, m)
                    else:
                        v2 = "{}.{}.{}".format(1, 0, 0)

        comp1 = SemanticVersionComparator( \
            {"operator": ">=", "version": v1, "pre_release": pre, "build": build,
             "logical_or": logical_or, "raw_string": raw_string})
        comp2 = SemanticVersionComparator(
            {"operator": "<", "version": v2, "pre_release": pre, "build": build,
             "logical_or": logical_or, "raw_string": raw_string})

        return comp1, comp2

    def __zeroPadVersion(self, version_str):
        try:
            major, minor, patch = version_str.split(".")

            if (major in self.wildcards) or (minor in self.wildcards) or (patch in self.wildcards):
                raise SyntaxError("version '{}' contains wildcards symbols and cannot be zero padded".format(version_str))
        except ValueError:
            patch = 0

            try:
                major, minor = version_str.split(".")

                if (major in self.wildcards) or (minor in self.wildcards):
                    raise SyntaxError(
                        "version '{}' contains wildcards symbols and cannot be zero padded".format(version_str))

            except ValueError:
                minor = 0
                major = version_str

                if (major in self.wildcards):
                    raise SyntaxError(
                        "version '{}' contains wildcards symbols and cannot be zero padded".format(version_str))

        return "{}.{}.{}".format(major, minor, patch)

    def simpleComparators(self, comparator):
        comp_cp = {}
        for k, v in comparator.items():
            if v is not None:
                comp_cp.update({k: v})
            else:
                comp_cp.update({k: ""})

        version = comp_cp["ver_num"]
        pre = comp_cp["pre"]
        build = comp_cp["build"]
        raw_string = comp_cp["simple"]
        logical_or = comparator["logical_or"]
        operator = comp_cp["operator"]

        try:
            if comp_cp["operator"] == "~":
                try:
                    return self.__unpackTilde(version, pre, build, logical_or, raw_string)
                except:
                    pass
            elif comp_cp["operator"] == "^":
                try:
                    return self.__unpackCaret(version, pre, build, logical_or, raw_string)
                except:
                    pass
            elif comp_cp["operator"] in (">", "<", ">=", "<=", "=", ""):
                if comp_cp["operator"] in ("=", ""):
                    comp_cp["operator"] = "=="
                    
                    return self.__unpackExact(version, pre, build, logical_or, raw_string)

                try:
                    comp_cp["ver_num"] = self.__zeroPadVersion(comp_cp["ver_num"])
                except SyntaxError:
                    try:
                        return self.__unpackWildcards(version, pre, build, logical_or, raw_string)
                    except ValueError:
                        pass

            if comp_cp["operator"] in (None, ''):
                comp1 = SemanticVersionComparator(
                    {"operator": comp_cp["operator"], "version": comp_cp["ver_num"],
                     "pre_release": comp_cp["pre"], "build": comp_cp["build"],
                     "logical_or": comparator["logical_or"], "raw_string": comp_cp["simple"]})
            else:
                comp1 = SemanticVersionComparator(
                    {"operator": comp_cp["operator"], "version": comp_cp["ver_num"],
                     "pre_release": comp_cp["pre"], "build": comp_cp["build"],
                     "logical_or": comparator["logical_or"], "raw_string": comp_cp["simple"]})

            return comp1, comp1
        except KeyError:
            raise KeyError(
                "bad comparator format, must be a dictionary with fields 'simple', 'logical_or', 'operator', " +
                "'ver_num', 'pre' and 'build', but found {}:'{}'".format(
                    type(comparator), str(comparator)))


class SemanticVersionComparator(dict):
    # a semantic version comparator is composed of
    # an 'operator' field (>,<,>=,<=,=)
    # a 'version' field (major.minor.patch)
    # a 'pre_release' field (-prerelease)
    # a 'build' field (+build)

    def unpack(self):
        return self["operator"], self["version"], self["pre_release"], self["build"], self["raw_string"]

    def __hash__(self): return hash(id(self))

    def __eq__(self, x): return x is self

    def __ne__(self, x): return x is not self


if __name__ == "__main__":
    from versionrangeparser import NodeVersionRangeParser

    #range_ = "^2.0.0"
    range_ = "1.0.0-pre.1+build - 2.0.0-alpha+1 || ^3.0.0"
    versions = ("1.0.0", "1.1.0", "2.0.0", "2.0.1", "2.1.0", "2.1.1", "3.0.1")

    nvrp = NodeVersionRangeParser()
    svr = nvrp.parse(range_)

    for v in versions:
        print(svr.compare(v))

    exit(0)

    #satisf = []
    #for v in svr.satisfies(versions):
        #satisf.append(v)
        #print(str(v))

    print("versions '{}' satisfy range '{}' over set of versions '{}'".format(satisf, range_,
                                                                              versions))
    print("version '{}' best satisfy range '{}' over set of versions '{}'".format(svr.best_satisfies(versions), range_,
                                                                                  versions))

    #"1.0.4 - 2.x"
    #">=1.0.0 <3.1.1"
    range_ = "1.0.4 - 2.x || ~2.0 || >= 3.2.9-alpha.4 <4.0.0-beta.5 || 2 || 2.1 || 2.2.2"
    #"~2.0"
    #"0.0.3"
    #range_ = "~2.0"
    versions = ("1.0.0", u"0.0.3", "0.0.4", "3.5.7", "2.0", "1.0.2-beta.5+build.2", "2.1-rc2")

    nvrp = NodeVersionRangeParser()
    svr = nvrp.parse(range_)

    #for sat in svr.satisfies(["1.0.0", "1.0.2-beta.5+build.2", "2.0", "2.1-rc2", "3.5.7"]):
    #    print(sat)

    print("version '{}' best satisfy range '{}' over set of versions '{}'".format(svr.best_satisfies(versions), range_, versions))

    t = None
    times = 10000
    begin = time.time()
    for r in range(times):
        svr.best_satisfies(["1.0.0", "1.0.2-beta.5+build.2", "2.0", "2.1-rc2", "3.5.7"])
    end = time.time()
    print("{} seconds to find {} times the best version satisying range '{}' over set of versions '{}'".format((end - begin), times, range_, versions))
