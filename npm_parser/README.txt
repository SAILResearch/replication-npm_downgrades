1) To install the parser, please run:

   $ python3 setup.py install --user

This procedure should install two required libraries, namely kids.cache and parsimonious. The former is used to enhance the parser performance by caching strings that were previously parsed and the latter is used to build the parser from the node-semver grammar (https://docs.npmjs.com/misc/semver).

2) To test the semantic version parser, please run:

   $ python3 semanticversionparser.py

3) To test the version range parser, please run:

   $ python3 versionrangeparser.py
   
4) To cite this parser, please use the following reference:

Cogo, F. R., Oliva, G. A., & Hassan, A. E. (in press). An Empirical Study of Dependency Downgrades in the npm Ecosystem. _IEEE Transactions on Software Engineering_. doi: 10.1109/TSE.2019.2952130.
