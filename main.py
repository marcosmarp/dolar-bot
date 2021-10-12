from functions import run_bot, init_praw


reddit_handler = init_praw()
argentina_subreddit = reddit_handler.subreddit("argentina")
republica_argentina_subreddit = reddit_handler.subreddit("republica_argentina")
test_subreddit = reddit_handler.subreddit("dolarbot")

while(True):
  run_bot([argentina_subreddit, republica_argentina_subreddit])

