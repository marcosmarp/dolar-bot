from praw import Reddit
from os import environ
from sys import stderr
from time import sleep, time
from praw.reddit import Subreddit
import pytz
from datetime import datetime
from requests import get
from bs4 import BeautifulSoup

def reset_timer():
  return time()

commands = ["!dolar", "!dólar"]
subreddits = ["RepublicaArgentina", "Republica_Argentina", "argentina"] # Display name is case sensitive
timers = dict.fromkeys(subreddits, reset_timer() - 600) # I discount the waiting time in the initial declaration so the first loop gets done immediately


def init_praw():
  return Reddit(
    client_id = environ['CLIENT_ID'],
    client_secret = environ['CLIENT_SECRET'],
    user_agent="console:dolar-bot:v1.0.0 (by u/dolar-bot)",
    username = "dolar-bot",
    password = environ['PASSWORD']
  )

def post_have_comments(post):
  return (post.num_comments > 0)

def AlreadyReplied(replies):
  for reply in replies:
    if reply.author.name == "dolar-bot":
      return True
  return False

def store_reply(comment):
  amount_of_lines = 0
  with open("replies.txt", "r", encoding='utf-8') as file_object:
    for line in file_object:
      amount_of_lines += 1
    file_object.close()
  with open("replies.txt", "a", encoding='utf-8') as file_object:
    file_object.write("Reply #" + str(int(amount_of_lines/8 + 1)))
    file_object.write("\n")
    file_object.write(" Replied comment data:")
    file_object.write("\n")
    file_object.write("   Author: " + comment.author.name)
    file_object.write("\n")
    file_object.write("   Link: https://www.reddit.com" + comment.permalink)
    file_object.write("\n")
    file_object.write("   Post:")
    file_object.write("\n")
    file_object.write("     Title: " + comment.submission.title)
    file_object.write("\n")
    file_object.write("     Author: " + comment.submission.author.name)
    file_object.write("\n")
    file_object.write("     Link: https://www.reddit.com" + comment.submission.permalink)
    file_object.write("\n")

def get_dolar_values():
  dolar_oficial_page = get("https://dolarhoy.com/cotizaciondolaroficial")
  dolar_blue_page = get("https://dolarhoy.com/cotizaciondolarblue")

  dolar_oficial_soup = BeautifulSoup(dolar_oficial_page.content, "html.parser")
  dolar_blue_soup = BeautifulSoup(dolar_blue_page.content, "html.parser")

  dolar_oficial_compra = dolar_oficial_soup.select('.value')[0].string
  dolar_oficial_venta = dolar_oficial_soup.select('.value')[1].string
  dolar_blue_compra = dolar_blue_soup.select('.value')[0].string
  dolar_blue_venta = dolar_blue_soup.select('.value')[1].string

  return [dolar_oficial_compra, dolar_oficial_venta, dolar_blue_compra, dolar_blue_venta]

def reply_comment(comment):
  dolar_values = get_dolar_values() 
  reply = "El dólar oficial cotiza a AR" + dolar_values[0] + " para compra y AR" + dolar_values[1] + " para venta" + "\n" + "\n"
  reply += "El dólar blue cotiza a AR" + dolar_values[2] + " para compra y AR" + dolar_values[3] + " para venta" + "\n" + "\n"
  reply += "Información actualizada al " + datetime.now(pytz.timezone('America/Argentina/Buenos_Aires')).strftime("%d/%m/%Y %H:%M:%S") + " desde [dólar hoy](https://dolarhoy.com/)" + "\n" + "\n"
  reply += "^(Soy un bot y esta acción fue realizada automáticamente)" + "\n" + "\n" + "^(Feedback? Bugs? )[^(Contactá al desarrollador)](mailto:marcosmartinezpalermo@gmail.com)" + "\n" + "\n" "[^(Github)](https://github.com/marcosmarp/dolar-bot)"
  comment.reply(reply)

def inform_reply_on_screen(comment):
  now = datetime.now(pytz.timezone('America/Argentina/Buenos_Aires'))
  dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
  print("           " + dt_string + ": replied " + comment.author.name + "'s comment", file=stderr)
  print("---------------", file=stderr)

def check_new_posts(posts):
  for post in posts:
    if post.author is None: # Check that the post wasn't deleted
      return

    print("Checking " + post.author.name + "'s '" + post.title + "' post", file=stderr)
    if not post_have_comments(post):
      log_err("Post doesn't have comments")
      return

    print(" Post has comments", file=stderr)

    for comment in post.comments:
      if comment.author is None: # Check that the comment wasn't deleted
        log_err("Comment was deleted")
        continue

      print("   Checking " + comment.author.name + "'s comment", file=stderr)
      if not hasattr(comment, "body"):
        log_err("Comment doesn't have body")
        continue

      print("     Comment has body", file=stderr)
      if not any(x in comment.body.lower() for x in commands):
        log_err("Comment doesn't mention '!dolar' or '!dólar'")
        continue

      print("       Comment mentions '!dolar' or '!dólar'", file=stderr)
      if AlreadyReplied(comment.replies):
        log_err("Comment already replied")
        continue

      print("         Comment yet to be replied", file=stderr)
      reply_comment(comment)
      inform_reply_on_screen(comment)
      store_reply(comment)
      reset_timers(post.subreddit.display_name, timers)

def reset_timers(subreddit_name, timers):
  if subreddit_name in timers:
    timers[subreddit_name] = reset_timer() 


def log_err(string):
  print(string, file=stderr)
  print("---------------", file=stderr)

def run_bot(subreddits_handler):
  if time() - timers.argentina >= 600:
    check_new_posts(subreddits_handler[0].new(limit=5))
  if time() - timers.Republica_Argentina >= 600:
    check_new_posts(subreddits_handler[1].new(limit=5))
  if time() - timers.RepublicaArgentina >= 600:
    check_new_posts(subreddits_handler[2].new(limit=5))
