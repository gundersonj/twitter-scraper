import pandas as pd
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Firefox
from dotenv import load_dotenv
import os

load_dotenv()

URL = 'https://www.twitter.com/login'
driver = Firefox()


def get_tweet_data(card):
    """Extract data from tweet data"""
    username = card.find_element_by_xpath('.//span').text
    handle = card.find_element_by_xpath('.//span[contains(text(), "@")]').text
    try:
        post_date = card.find_element_by_xpath(
            './/time').get_attribute('datetime')
    except NoSuchElementException:
        return
    comment = card.find_element_by_xpath(
        './/div[1]/div[1]/div[1]/div[2]/div[2]/div[2]/div[1]').text
    responding = card.find_element_by_xpath(
        './/div[1]/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]').text
    tweet_text = comment + responding
    reply_count = card.find_element_by_xpath(
        './/div[@data-testid="reply"]').text
    retweet_count = card.find_element_by_xpath(
        './/div[@data-testid="retweet"]').text
    like_count = card.find_element_by_xpath('.//div[@data-testid="like"]').text

    tweet = (username, handle, post_date, tweet_text,
             reply_count, retweet_count, like_count)
    return tweet


def write_to_excel(data):
    df = pd.DataFrame(data, index=None)
    df.columns = ['Username', 'Handle', 'Post Date',
                  'Tweet Text', 'Comments', 'Retweets', 'Likes']
    df.to_excel('tweets.xlsx', index=None)


def main():
    # Navigate to twitter
    driver.get(URL)
    driver.maximize_window()
    sleep(5)

    # Login
    username = driver.find_element_by_xpath('//input[@name="username"]')
    username.send_keys(os.getenv('USER'))
    username.send_keys(Keys.RETURN)
    sleep(5)

    password = driver.find_element_by_xpath('//input[@name="password"]')
    password.send_keys(os.getenv('PASSWD'))
    password.send_keys(Keys.RETURN)
    sleep(5)

    # Enter search term
    search_input = driver.find_element_by_xpath(
        '//input[@aria-label="Search query"]')
    search_input.send_keys(
        '(dredging AND project) OR (#dredge OR #dredging) until:2021-10-16 since:2021-07-01')

    search_input.send_keys(Keys.RETURN)
    sleep(5)

    # Navigate to latest tab
    driver.find_element_by_link_text('Latest').click()
    sleep(2)

    # Extract available tweets on page
    tweet_data = []
    tweet_ids = set()
    last_position = driver.execute_script("return window.pageYOffset;")
    scrolling = True

    while scrolling:
        page_cards = driver.find_elements_by_xpath(
            '//article[@data-testid="tweet"]')
        for card in page_cards[-15:]:
            tweet = get_tweet_data(card)
            if tweet:
                tweet_id = ''.join(tweet)
                if tweet_id not in tweet_ids:
                    tweet_ids.add(tweet_id)
                    tweet_data.append(tweet)

        scroll_attempt = 0
        while True:
            # Scroll down the page
            driver.execute_script(
                'window.scrollTo(0, document.body.scrollHeight);')
            sleep(2)

            # Check scroll position
            current_position = driver.execute_script(
                "return window.pageYOffset;")
            if last_position == current_position:
                scroll_attempt += 1

                # End of scroll region
                if scroll_attempt >= 3:
                    scrolling = False
                    break
                else:
                    sleep(2)  # attempt to scroll again
            else:
                last_position = current_position
                break

    write_to_excel(tweet_data)


if __name__ == '__main__':
    main()
