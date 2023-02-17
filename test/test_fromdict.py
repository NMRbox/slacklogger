import logging
import os
import unittest

from nmrbox_slack import LazySlackHandler, from_mapping

TOKEN_FILE = "token.dat"
class FromDict(unittest.TestCase):

    def test_build(self) -> None:
        logging.basicConfig()
        if not os.path.isfile(TOKEN_FILE):
            raise ValueError(f"Create {TOKEN_FILE} before running test")

        mapping = {'slack': {'channel':'logging','token file':TOKEN_FILE}}
        lazy = from_mapping(mapping,lazy=True)
        self.assertIsInstance(lazy,LazySlackHandler)
        regular = from_mapping(mapping,lazy=False)
        tlogger = logging.getLogger("Test Logger")
        tlogger.propagate = False
        tlogger.setLevel(logging.WARN)
        tlogger.addHandler(regular)
        tlogger.warning("API test")
