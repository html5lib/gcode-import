import sys
import os
import glob
import unittest

def buildTestSuite():
    suite = unittest.TestSuite()
    for testcase in glob.glob('test_*.py'):
        module = os.path.splitext(testcase)[0]
        suite.addTest(__import__(module).buildTestSuite())
    return suite

def main():
    unittest.TextTestRunner().run(buildTestSuite())

if __name__ == "__main__":
    main()
