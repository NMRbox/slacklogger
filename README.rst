Slack logger
============

This package provides a logging.Handler that will send message to a
slack channel. Supports updated *slack.WebClient* API released in 2019.

Authorization
-------------

See https:://api.slack.com to for information on setting up app and get
an authorization token. Only a "bot" token is required to use
SlackHandler, however, the unittest is more comlete with a "user" token.

Limitations
-----------

How often messages can be sent is limited by slack. See
https://api.slack.com/docs/rate-limits. By default, this handler only
sends accumulated messages every 60 seconds. That can be adjusted by the
optional *update* argument to **SlackHandler**.

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

Funding acknowledgment
~~~~~~~~~~~~~~~~~~~~~~

This work supported by National Institutes of Health (NIH) / National
Institute of General Medical Sciences (NIGMS), grant 1P41GM111135.
