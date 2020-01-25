import io
import logging
import slack
import sys
import time


class SlackHandler(logging.StreamHandler):
    """Python logging handler that posts to a slack channel.
    Rate limited; slack not intended for rapid automated use and posting too often can result in dropped messages"""

    def __init__(self, token, channel_name: str, *, update: int = 60, timeout: int = None) -> None:
        """
        :param token: Slack bot or user token
        :param channel_name: channel to post to
        :param update: how many seconds to wait before updating slack channel. must be >= 1
        :param timeout: optional timeout in seconds to wait when posting
        """
        super().__init__(stream=self)
        try:
            assert isinstance(update, int)
            if update < 1:
                raise ValueError("Update must be at least {:d} second".format(update))
            self.update = update
            self.timeout = timeout
            self.client = slack.WebClient(token)
            self.buffer = io.StringIO()
            self.send_time = 0  # don't send unit past this time (epoch seconds)
            response = self.client.channels_list()
            if response['ok']:
                channels = response['channels']
                channel_search = [c for c in channels if c['name'] == channel_name]
                if channel_search:
                    self.channel = channel_search[0]
                    self.channel_id = self.channel['id']
                else:
                    raise ValueError("Couldn't find channel {}".format(channel_name))
            else:
                raise ValueError("Couldn't get channel list")
        except Exception as e:
            raise e

    def write(self, msg):
        """Implement stream method"""
        print(msg, file=self.buffer)

    def flush(self) -> None:
        """Implement stream method
        Send if not too soon since last send
        """
        if self.send_time > time.time():
            return
        wait = self._flush()
        self.send_time = time.time() + max(self.update, int(wait))

    def _flush(self) -> int:
        """Attempt to send message
        :return 0 if message goes through, or how long slack said to wait if it doesn't
        """
        try:
            buffer_text = self.buffer.getvalue()
            if buffer_text:
                self.client.chat_postMessage(channel=self.channel_id, text=buffer_text, timeout=self.timeout)
                # stackoverflow indicates faster to create new object than reuse the old one
                self.buffer = io.StringIO()
            return 0
        except slack.errors.SlackApiError as sae:
            wait = sae.response.headers.get("Retry-After")
            if wait:
                return int(wait)
            raise sae

    def send_remaining(self):
        """Send remaining messages, sleeping until they all good through
        Intended for end of program.
        atexit doesn't work because other objects already shut down
        """
        while True:
            wait = self._flush()
            if wait == 0:
                return
            time.sleep(wait)


