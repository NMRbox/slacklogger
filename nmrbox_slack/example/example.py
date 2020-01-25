import logging
from nmrbox_slack.slacklogger import SlackHandler

if __name__ == "__main__":
    logging.basicConfig()
    try:
        token = 'xoxb-...'
        channel = 'channel-name'
        handler = SlackHandler(token, channel)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        example_logger = logging.getLogger("Test Logger")
        example_logger.propagate = False
        example_logger.addHandler(handler)
        example_logger.setLevel(logging.INFO)
        example_logger.info("Then shalt thou use Python three, no more, no less.")
        handler.send_remaining()

    except Exception as e:
        print(e)
        raise e
