Slack logger
============

This package provides logging.Handler implementations that will send message to a
slack channel. Supports updated *slack.WebClient* API released in 2020.

Authorization
-------------

See https:://api.slack.com to for information on setting up app and get
an authorization token. Only a "bot" token is required to use
SlackHandler, however, the unittest is more complete with a "user" token.

Limitations
-----------

How often messages can be sent is limited by slack. See
https://api.slack.com/docs/rate-limits. By default, this handler only
sends accumulated messages every 60 seconds. That can be adjusted by the
optional *update* argument to **SlackHandler**.

*send_remaining()* should be called prior to program exit to send any remaining 
messages.

Example
~~~~~~~

::

    from nmrbox_slack.slacklogger import SlackHandler
    token = 'your token here'
    channel = 'your channel name'
    handler = SlackHandler(token, channel)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    example_logger = logging.getLogger("Test Logger")
    example_logger.propagate = False
    example_logger.addHandler(handler)
    example_logger.setLevel(logging.INFO)
    example_logger.info("Then shalt thou use Python three, no more, no less.")
    ...
    # at end of program
    handler.send_remaining()

Variants
~~~~~~~~
Two versions are currently supported.

- **SlackHandler** connects to slack upon creation and validates the token and channel name.
- **LazySlackHandler** does not attempt to connect to slack until the first message is sent.

SlackHandler is recommended if it is known messages are to be sent. LazySlackHandler is available
to reduce overhead of processes which typically do not send messages.

Additional channels
~~~~~~~~~~~~~~~~~~~
Sending to additional channels may be done more efficiently with the *SlackHandler.additional_channel_handler()*
method.

::

    from nmrbox_slack.slacklogger import SlackHandler
    token = 'your token here'
    channel = 'your channel name'
    handler = SlackHandler(token, channel)
    second_handler = heandler.additional_channel_handler('second channel name')


Funding acknowledgment
~~~~~~~~~~~~~~~~~~~~~~

This work supported by National Institutes of Health (NIH) / National
Institute of General Medical Sciences (NIGMS), grant 1P41GM111135.
