"""
File: final_project.py
---------------
This program will read information from a Twitter API and gather the information
for an specific company/person requested by the user and analyze the tweets with
some visual tools (graphs)
"""

# Libraries needed for this project
import re
import json
import tweepy as tw
from textblob import TextBlob
import pandas as pd
import matplotlib.pyplot as plt

# Constants
MAX_TWEETS_ANALYSIS = 500

def main ():
    # Gather the tweets from the API
    (tweets, user_search) = run_twitter_API()

    # Validate if the API returned information
    if tweets != None:
        # Parse the information included in the tweets
        parsed_tweets = parse_tweets(tweets)

        # Validation to avoid bug when there are no tweets after parse
        if len(parsed_tweets) != 0:
            positive_lbl = "Positive Tweets"
            negative_lbl = "Negative Tweets"

            # Get positive tweets in a list and calculate percentage
            positive_tweets = [tweet for tweet in parsed_tweets if tweet['sentiment'] == 'positive']
            percentage_positive_tweets = "{:.2f}".format(100*len(positive_tweets)/len(parsed_tweets))
            print(positive_lbl + " : " + str(percentage_positive_tweets))

            # Get negative tweets in a list and calculate percentage
            negative_tweets = [tweet for tweet in parsed_tweets if tweet['sentiment'] == 'negative']
            percentage_negative_tweets = "{:.2f}".format(100*len(negative_tweets)/len(parsed_tweets))
            print(negative_lbl + " : " + str(percentage_negative_tweets))

            # Initialize the dict that will be on the visualization
            data_to_graph={}

            # Assign values
            data_to_graph["Type"] = [positive_lbl,negative_lbl]
            data_to_graph["Percentage"] = [percentage_positive_tweets,percentage_negative_tweets]

            # Visualization of the information returned
            create_pie_chart(data_to_graph, user_search)

        else:
            # Keep participating message
            print("No data to analyze. Sorry ! ... get more followers by the way =P ")

"""
PRE:  There is a need of tweets information to analyze based on user input (company/person) 
POST: Information extracted from Twitter API and returned
"""
def run_twitter_API():
    # Initialize the authorization variables with values from file
    # to avoid showing sensitive information in the code
    with open("api_config.json", "r") as json_data:
        data = json.load(json_data)
        consumer_key= data["consumer_key"]
        consumer_secret= data["consumer_secret"]
        access_token= data["access_token"]
        access_token_secret= data["access_token_secret"]

    try:
        # Set the authorization and API variable
        auth = tw.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tw.API(auth, wait_on_rate_limit=True)

        # Validation code to check that there is communication with Twitter
        # Post a tweet from Python
        # api.update_status("Look, I'm tweeting from #Python !")
        # Your tweet has been posted!

        # Variables needed for the API call
        search_words = input("Give a company for the analysis (use the Twitter format ex.: @dominos) : ")
        # Only tweets from this year
        date_since = "2020-01-01"

        # Collect the tweets
        tweets = tw.Cursor(api.search,
                  q=search_words,
                  lang="en",
                  since=date_since).items(MAX_TWEETS_ANALYSIS)

        # Return the result of the tweets
        return tweets, search_words

    except tw.TweepError as err_msg:
        print("Error : " + str(err_msg))
        return None

"""
PRE:  Tweet contain extra information not needed
POST: The function will clean tweet text by removing links, special characters using simple regex statements.
"""
def clean_tweet(tweet_text):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet_text).split())

"""
PRE:  Review each tweet and analyze the content of the text
POST: The function will return if the comment in the tweet is positive or negative
"""
def get_tweet_sentiment(tweet_text):
        # Create TextBlob object of passed tweet text
        analysis = TextBlob(clean_tweet(tweet_text))

        # Using textblob's sentiment method, the function will return positive or negative
        if analysis.sentiment.polarity >= 0:
            return 'positive'
        else:
            return 'negative'

"""
PRE:  Tweets are in raw with a lot of extra information
POST: Tweets are parsed, clean and easy to manipulate the results to analysis
"""
def parse_tweets(tweets):
    # List of tweets parsed
    parsed_tweets = []

    # Loop to parse all the tweets
    for tweet in tweets:
        # Create empty dict for each tweet
        process_tweet = {}

        # Get the text of the tweet and store in the dictionary
        process_tweet['text'] = tweet.text

        # Get the sentiment of the tweet
        process_tweet['sentiment'] = get_tweet_sentiment(process_tweet['text'])

        # Append parsed tweets to the list
        if tweet.retweet_count > 0:
            # If tweet has re-tweets, just append one time
            if process_tweet not in parsed_tweets:
                parsed_tweets.append(process_tweet)
        else:
            parsed_tweets.append(process_tweet)

    # return parsed tweets
    return parsed_tweets

"""
PRE:  The analysis is done and a good visualization is needed
POST: A pie chart is created to show the results to the user
"""
def create_pie_chart(data_to_graph, user_search):
    # Assign the data to the graph
    df = pd.DataFrame(data_to_graph)
    sums = df.Percentage.groupby(df.Type).sum()

    # Format and generation of the pie chart
    explode = (0.1, 0.1)
    colors = ['#ff9999', '#66b3ff']
    plt.pie(sums, colors=colors, explode=explode, labels=sums.index, autopct='%1.2f%%', shadow=False, startangle=140, pctdistance=0.85)
    plt.title("Public Acceptance on Twitter 2020 : " + user_search)

    # Draw circle for nicer visualization
    centre_circle = plt.Circle((0,0),0.70,fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    plt.axis('equal')

    # Show visualization
    plt.show()

if __name__ == '__main__':
    main()
