import configparser
import logging
import os
import time
import traceback
import unittest
import warnings
from collections import defaultdict

from nmrbox_slack.slacklogger import SlackHandler, LazySlackHandler


class SlackLogger(unittest.TestCase):

    def setUp(self) -> None:
        logging.basicConfig()
        config = configparser.ConfigParser( )
        if not os.path.exists('test.cfg'):
            raise ValueError("Create test.cfg before running unit tests")
        with open('test.cfg') as f:
            config.read_file(f)
        token = config['slacktest']['token']
        self.user_token = token.startswith('xoxp')
        channel = config['slacktest']['channel']
        second_channel = config['slacktest']['second channel']
        self.number_messages = config.getint('slacktest','number messages',fallback=5)
        first_handler = SlackHandler(token,channel)
        self.handlers = (first_handler,
                         first_handler.additional_channel_handler(second_channel),
                         LazySlackHandler(token, channel))
        if not self.user_token:
            if token.startswith('xoxb'):
                warnings.warn("Bot token does not support read back of messages, check slack channel manually.")
            else:
                warnings.warn('Unrecognized token type "{}". Check slack channel manually.'.format(token[:4]))

    def test_send(self):
        self.handler_sent = {}
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        tlogger = logging.getLogger("Test Logger")
        tlogger.propagate = False
        tlogger.setLevel(logging.WARN)
        tlogger.info("This should not appear")
        tlogger.setLevel(logging.INFO)
        for h in self.handlers:
            sent_messages = []
            h.setFormatter(formatter)
            tlogger.addHandler(h)
            for i in range(0, self.number_messages):
                msg = "message # {:d}".format(i)
                tlogger.info(msg)
                if self.user_token:
                    sent_messages.append(msg)
            self.handler_sent[type(h)] = sent_messages

    def tearDown(self) -> None:
        for h in self.handlers:
            h.send_remaining()
            if self.user_token:
                sent_messages = self.handler_sent[type(h)]
                response = h.webclient.channels_history(channel=h.channel_id,count=self.number_messages)
                msgs = response['messages']
                for msg in msgs:
                    msg_text = msg['text']
                    sent_messages = [m for m in sent_messages if not m in msg_text]
                if sent_messages:
                    raise AssertionError("Messages {} not read back from test channel".format(','.join(sent_messages)))

