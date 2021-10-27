from functions import run_bot, init_praw, stderr


reddit_handler = init_praw()
argentina_subreddit = reddit_handler.subreddit("argentina")
test_subreddit = reddit_handler.subreddit("dolarbot")

while(True):
  try:
    run_bot(test_subreddit)
  except KeyboardInterrupt: # For quitting with ctrl+C
    break
  except:
    print("Reddit exception")
