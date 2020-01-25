import configparser
import logging
import os
import time
import unittest
import warnings

from nmrbox_slack.slacklogger import SlackHandler

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
        self.channel = config['slacktest']['channel']
        self.number_messages = config.getint('slacktest','number messages',fallback=5)
        self.handler = SlackHandler(token,self.channel)
        if not self.user_token:
            if token.startswith('xoxb'):
                warnings.warn("Bot token does not support read back of messages, check slack channel manually.")
            else:
                warnings.warn('Unrecognized token type "{}". Check slack channel manually.'.format(token[:4]))

    def test_send(self):
        self.sent_messages = []
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.handler.setFormatter(formatter)
        tlogger = logging.getLogger("Test Logger")
        tlogger.propagate = False
        tlogger.addHandler(self.handler)
        tlogger.setLevel(logging.WARN)
        tlogger.info("This should not appear")
        tlogger.setLevel(logging.INFO)
        for i in range(0, self.number_messages):
            msg = "message # {:d}".format(i)
            tlogger.info(msg)
            if self.user_token:
                self.sent_messages.append(msg)

    def tearDown(self) -> None:
        self.handler.send_remaining()
        if self.user_token:
            response = self.handler.client.channels_history(channel=self.handler.channel_id,count=self.number_messages)
            msgs = response['messages']
            for msg in msgs:
                msg_text = msg['text']
                self.sent_messages = [m for m in self.sent_messages if not m in msg_text]
            if self.sent_messages:
                raise AssertionError("Messages {} not read back from test channel".format(','.join(self.sent_messages)))
