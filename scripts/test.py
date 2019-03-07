# -*- coding: UTF-8 -*-

import os
import unittest


if __name__ == "__main__":
    test_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "test")
    suite = unittest.TestLoader().discover(test_directory, pattern="*.py")
    unittest.TextTestRunner(verbosity=2).run(suite)