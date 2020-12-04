import configparser
import logging
import os
import time
import traceback
import unittest
import warnings
from collections import defaultdict

from nmrbox_slack.slacklogger import SlackHandler, LazySlackHandler


class LazySlackLogger(unittest.TestCase):

    def test_create(self):
        lh = LazySlackHandler('abc','xyz')
        assert lh._handler is None
