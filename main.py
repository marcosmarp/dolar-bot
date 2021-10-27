from functions import log_error, run_bot, init_praw
from traceback import print_exc


reddit_handler = init_praw()
argentina_subreddit = reddit_handler.subreddit("argentina")
test_subreddit = reddit_handler.subreddit("dolarbot")

while(True):
  try:
    run_bot(argentina_subreddit)
  except KeyboardInterrupt: # For quitting with ctrl+C
    break
  except:
    log_error("Reddit exception: ")
    print_exc()
    
