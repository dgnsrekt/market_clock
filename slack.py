from market_clock.regions import EXCHANGES
from market_clock.cache import RedisCache
from decouple import config
from notifiers.providers.slack import Slack
from loguru import logger

import time

SLACK_WEBHOOK_TOKEN = config("SLACK_WEBHOOK_TOKEN")
SLACK_WEBHOOK = f"https://hooks.slack.com/services/{SLACK_WEBHOOK_TOKEN}"

MINUTES = config("MINUTES", cast=int)


def main():
    slack_client = Slack()

    for region in EXCHANGES:
        region.update()

        if not region.is_open:
            logger.info(f"{region.name.upper()} MARKET CLOSED")
            logger.info(f"{region.time_to_open.in_words()} to the Opening Bell")

            if region.time_to_open.in_minutes() <= MINUTES:
                if not RedisCache.check_opening_message_sent(region.name.upper()):
                    message = f"[{region.name}] - {region.exchange} exchange opening in {region.time_to_open.in_words()}"
                    slack_client.notify(message=message, webhook_url=SLACK_WEBHOOK)
                    RedisCache.add_opening(region.name.upper())
                    logger.info(message)
                    time.sleep(1)

        if region.is_open:
            logger.info(f"{region.name.upper()} MARKET OPEN")
            logger.info(f"{region.time_to_close.in_words()} to the Closing Bell")

            if region.time_to_close.in_minutes() <= MINUTES:
                if not RedisCache.check_closing_message_sent(region.name.upper()):
                    message = f"[{region.name}] - {region.exchange} exchange closing in {region.time_to_close.in_words()}"
                    slack_client.notify(message=message, webhook_url=SLACK_WEBHOOK)
                    RedisCache.add_closing(region.name.upper())
                    logger.info(message)
                    time.sleep(1)


if __name__ == "__main__":
    while True:
        main()
        time.sleep(60)
