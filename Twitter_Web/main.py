import csv
from time import sleep
from msedge.selenium_tools import Edge, EdgeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common import exceptions
from flask import Flask, render_template

def create_webdriver_instance():
    # Created a web driver instance from msedge
    options = EdgeOptions()
    options.use_chromium = True
    driver = Edge(options=options)
    return driver


def login_to_twitter(username, password, driver):
    url = 'https://twitter.com/login'
    try:
        driver.get(url)
        driver.maximize_window()
        xpath_username = '//input[@name="session[username_or_email]"]'
        # We wait for max 10 seconds for username_or_email section to load, if it does'nt we get an Timeout exception
        WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, xpath_username)))
        uid_input = driver.find_element_by_xpath(xpath_username)
        uid_input.send_keys(username)
    except exceptions.TimeoutException:
        print("Timeout while waiting for Login screen")

    pwd_input = driver.find_element_by_xpath('//input[@name="session[password]"]')
    pwd_input.send_keys(password)
    try:
        pwd_input.send_keys(Keys.RETURN)
        url = "https://twitter.com/home"
        WebDriverWait(driver, 10).until(expected_conditions.url_to_be(url))
    except exceptions.TimeoutException:
        print("Timeout while waiting for home screen")


def find_search_input_and_enter_criteria(search_term, driver):
    # Sends the term we want to search on Twitter
    xpath_search = '//input[@aria-label="Search query"]'
    WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located((By.XPATH, xpath_search)))
    search_input = driver.find_element_by_xpath(xpath_search)
    search_input.send_keys(search_term)
    search_input.send_keys(Keys.RETURN)


def find_tweets():
    # Locates tweets and returns them
    tweet_xpath = '//div[@data-testid="tweet"]'
    tweets = driver.find_elements_by_xpath(tweet_xpath)
    return tweets


def collect_data(tweets):
    # We get the data needed from those tweets and save them in a list
    tweet_pool = []
    for i in range(5):
        tweet = tweets[i]

        Tweetwers_Name = tweet.find_element_by_xpath('.//span').text
        Time_Stamp = tweet.find_element_by_xpath('.//time').get_attribute('datetime')
        Contents = tweet.find_element_by_xpath('.//div[2]/div[2]/div[1]').text
        Responding = tweet.find_element_by_xpath('.//div[2]/div[2]/div[2]').text
        Full_Tweet = Contents + Responding

        Reply = tweet.find_element_by_xpath('.//div[@data-testid="reply"]').text
        Retweets = tweet.find_element_by_xpath('.//div[@data-testid="retweet"]').text
        Likes = tweet.find_element_by_xpath('.//div[@data-testid="like"]').text

        full_data = [Tweetwers_Name, Time_Stamp, Full_Tweet, Reply, Retweets, Likes]

        tweet_pool.append(full_data)

    return tweet_pool


def write_to_csv():
    # After gathering the data, we write the  'tweet_pool' list into a csv file
    with open('tweet_pool.csv', 'w', newline='', encoding='utf-8') as f:
        header = ['Author', 'Timestamp', 'Contents', 'ReplysCount', 'RetweetCount', 'LikeCount']
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(tweet_pool)


def display(tweet_pool):
    # Displays the 'tweet_pool'
    for i in range(len(tweet_pool)):
        print(tweet_pool[i])
        print("\n")


def display_on_web_interface():
    # Finally, using Flask we can display the csv file with a simple web interface
    app = Flask(__name__)

    with open('tweet_pool.csv', 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)

        data = []

        for line in csv_reader:
            data.append((line['Author'], line['Timestamp'], line['Contents'], line['ReplysCount'], line['RetweetCount'], line['LikeCount']))



    headings = ("Author", "Timestampt",
                "Contents ", "ReplysCount ", "RetweetCount ", "LikeCount ")



    @app.route("/")
    def home():
        return render_template("index.html", headings=headings, data=data)

    app.run()



driver = create_webdriver_instance()
login_to_twitter('ApBot8', 'thisisapassword', driver)
find_search_input_and_enter_criteria('requestforstartup', driver)
sleep(3)
driver.find_element_by_link_text('Latest').click()
sleep(5)
tweets = find_tweets()
tweet_pool = collect_data(tweets)
display(tweet_pool)
write_to_csv()
display_on_web_interface()
# URL is http://127.0.0.1:5000/
# Reminder:csv file may look empty, need to refresh the page.

