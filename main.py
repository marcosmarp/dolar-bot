from functions import run_bot, init_praw, stderr


reddit_handler = init_praw()
argentina_subreddit = reddit_handler.subreddit("argentina")
test_subreddit = reddit_handler.subreddit("dolarbot")

while(True):
  try:
    run_bot(argentina_subreddit)
  except:
    print("Reddit exception", file=stderr)
