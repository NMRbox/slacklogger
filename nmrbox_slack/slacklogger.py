import collections
import io
import logging
from abc import ABC, abstractmethod

import slack
import sys
import time

from slack import WebClient


class _HandlerCore:

    def __init__(self, token):
        try:
            self.client = slack.WebClient(token)
            response = self.client.conversations_list(types="public_channel,private_channel")
            if response['ok']:
                channelresp = response['channels']
                self._channels = {c['name']: c['id'] for c in channelresp}
        except Exception as e:
            raise e

    def channel_id(self, channelname: str) -> str:
        return self._channels[channelname]


class AbstractSlackHandler(logging.StreamHandler, ABC):
    """Python logging handler that posts to a slack channel.
    Rate limited; slack not intended for rapid automated use and posting too often can result in dropped messages"""

    def __init__(self, *, update: int = 60, timeout: int = None) -> None:
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
            self.buffer = io.StringIO()
            self.send_time = 0  # don't send unit past this time (epoch seconds)
        except Exception as e:
            raise e

    @property
    @abstractmethod
    def channel_id(self) -> str:
        """Channel id for channel_name passed at construction"""
        pass

    @property
    @abstractmethod
    def webclient(self) -> WebClient:
        """client object from Slack API"""
        pass

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
                self._post_message(text=buffer_text, timeout=self.timeout)
                # stackoverflow indicates faster to create new object than reuse the old one
                self.buffer = io.StringIO()
            return 0
        except slack.errors.SlackApiError as sae:
            wait = sae.response.headers.get("Retry-After")
            if wait:
                return int(wait)
            raise sae

    @abstractmethod
    def _post_message(self, text: str, timeout: int):
        pass

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


class _ConnectedSlackHandler(AbstractSlackHandler):
    """shared _HandlerCore"""

    def __init__(self, handlercore:_HandlerCore,channel_name:str,**kwargs):
        """
        :param token: Slack bot or user token
        :param channel_name: channel to post to
        :param update: how many seconds to wait before updating slack channel. must be >= 1
        :param timeout: optional timeout in seconds to wait when posting
        """
        super().__init__(**kwargs)
        self.handler = handlercore
        self.channel = self.handler.channel_id(channel_name)

    @property
    def webclient(self) -> WebClient:
        return self.handler.client

    @property
    def channel_id(self):
        return self.channel

    def _post_message(self, text: str, timeout: int):
        self.handler.client.chat_postMessage(channel=self.channel_id, text=text, timeout=timeout)

class SlackHandler(_ConnectedSlackHandler):
    """Validates connection and channel upon creation"""

    def __init__(self, token, channel_name, **kwargs):
        """
        :param token: Slack bot or user token
        :param channel_name: channel to post to
        :param update: how many seconds to wait before updating slack channel. must be >= 1
        :param timeout: optional timeout in seconds to wait when posting
        """
        super().__init__(_HandlerCore(token),channel_name,**kwargs)

    def additional_channel_handler(self, channel_name)->AbstractSlackHandler:
        """
        Return handler for another channel
        """
        return _ConnectedSlackHandler(self.handler,channel_name)


class LazySlackHandler(AbstractSlackHandler):
    """Does not connect to slack until first message. Useful for processes that don't send messages
    under normal circumstances."""

    def __init__(self, token, channel_name, **kwargs):
        """
        :param token: Slack bot or user token
        :param channel_name: channel to post to
        :param update: how many seconds to wait before updating slack channel. must be >= 1
        :param timeout: optional timeout in seconds to wait when posting
        """
        super().__init__(**kwargs)
        self.token = token
        self.channel_name = channel_name
        self._handler = None
        self._channel_id = None

    @property
    def webclient(self) -> WebClient:
        return self.handler.client

    @property
    def channel_id(self):
        if self._channel_id is None:
            self._channel_id = self.handler.channel_id(self.channel_name)
        return self._channel_id

    @property
    def handler(self) -> _HandlerCore:
        """Lazily created handler"""
        if self._handler is None:
            self._handler = _HandlerCore(self.token)
        return self._handler

    def _post_message(self, text: str, timeout: int):
        self.handler.client.chat_postMessage(channel=self.channel_id, text=text, timeout=timeout)
