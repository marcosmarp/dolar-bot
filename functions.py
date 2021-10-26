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

def init_praw():
  return Reddit(
    client_id = environ['CLIENT_ID'],
    client_secret = environ['CLIENT_SECRET'],
    user_agent="console:dolar-bot:v1.1.0 (by u/dolar-bot)",
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
  dolar_bolsa_page = get("https://dolarhoy.com/cotizaciondolarbolsa")
  dolar_ccl_page = get("https://dolarhoy.com/cotizaciondolarcontadoconliqui")
  dolar_solidario_page = get("https://dolarhoy.com/cotizaciondolarturista")
  dolar_turista_page = get("https://dolarhoy.com/cotizaciondolarsolidario")

  dolar_oficial_soup = BeautifulSoup(dolar_oficial_page.content, "html.parser")
  dolar_blue_soup = BeautifulSoup(dolar_blue_page.content, "html.parser")
  dolar_bolsa_soup = BeautifulSoup(dolar_bolsa_page.content, "html.parser")
  dolar_ccl_soup = BeautifulSoup(dolar_ccl_page.content, "html.parser")
  dolar_solidario_soup = BeautifulSoup(dolar_solidario_page.content, "html.parser")
  dolar_turista_soup = BeautifulSoup(dolar_turista_page.content, "html.parser")

  dolar_oficial_compra = dolar_oficial_soup.select('.value')[0].string
  dolar_oficial_venta = dolar_oficial_soup.select('.value')[1].string
  dolar_blue_compra = dolar_blue_soup.select('.value')[0].string
  dolar_blue_venta = dolar_blue_soup.select('.value')[1].string
  dolar_bolsa_compra = dolar_bolsa_soup.select('.value')[0].string
  dolar_bolsa_venta = dolar_bolsa_soup.select('.value')[1].string
  dolar_ccl_compra = dolar_ccl_soup.select('.value')[0].string
  dolar_ccl_venta = dolar_ccl_soup.select('.value')[1].string
  dolar_solidario_venta = dolar_solidario_soup.select('.value')[0].string
  dolar_turista_venta = dolar_turista_soup.select('.value')[0].string

  return [dolar_oficial_compra, dolar_oficial_venta, dolar_blue_compra, dolar_blue_venta, 
  dolar_bolsa_compra, dolar_bolsa_venta, dolar_ccl_compra, dolar_ccl_venta, dolar_solidario_venta, dolar_turista_venta]

def reply_comment(comment):
  dolar_values = get_dolar_values() 

  reply = """
  |Divisa|Compra|Venta|
  |:-|:-|:-|
  |**Oficial**|AR{0}|AR{1}|
  |**Blue**|AR{2}|AR{3}|
  |**MEP/Bolsa**|AR{4}|AR{5}|
  |**CCL**|AR{6}|AR{7}|'
  |**Solidario** (+30% impuestos)|\-|AR{8}|
  |**Ahorro/Tarjeta/Turista** (+64% impuestos)|\-|AR{9}|

  Información actualizada al {10} desde [dólar hoy](https://dolarhoy.com/)
  
  ^(Soy un bot y esta acción fue realizada automáticamente)
  
  ^(Feedback? Bugs?: )[^(Github)](https://github.com/marcosmarp/dolar-bot)
  """

  reply = reply.format(dolar_values[0], dolar_values[1], dolar_values[2], dolar_values[3], dolar_values[4], 
  dolar_values[5], dolar_values[6], dolar_values[7], dolar_values[8], dolar_values[9], 
  datetime.now(pytz.timezone('America/Argentina/Buenos_Aires')).strftime("%d/%m/%Y %H:%M:%S"))

  comment.reply(reply)
  sleep(5)

def inform_reply_on_screen(comment):
  now = datetime.now(pytz.timezone('America/Argentina/Buenos_Aires'))
  dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
  print("           " + dt_string + ": replied " + comment.author.name + "'s comment", file=stderr)
  print("---------------", file=stderr)

def check_new_posts(posts):
  for post in posts:
    if post.author is not None: # Check that the post wasn't deleted
      print("Checking " + post.author.name + "'s '" + post.title + "' post", file=stderr)
      if post_have_comments(post):
        print(" Post have comments", file=stderr)
        for comment in post.comments:
          if comment.author is not None: # Check that the comment wasn't deleted
            print("   Checking " + comment.author.name + "'s comment", file=stderr)
            if hasattr(comment, "body"):
              print("     Comment have body", file=stderr)
              if "!dolar" in comment.body.lower() or "!dólar" in comment.body.lower():
                print("       Comment mentions '!dolar' or '!dólar'", file=stderr)
                if not AlreadyReplied(comment.replies):
                  print("         Comment yet to be replied", file=stderr)
                  reply_comment(comment)
                  inform_reply_on_screen(comment)
                  store_reply(comment)
                  return
                else:
                  print("Comment already replied", file=stderr)
                  print("---------------", file=stderr)
              else: 
                print("Comment doesn't mention '!dolar' or '!dólar'", file=stderr)
                print("---------------", file=stderr)
            else:
              print("Comment doesn't have body", file=stderr)
              print("---------------", file=stderr)
          else:
            print("Comment was deleted", file=stderr)
            print("---------------", file=stderr)
      else:
        print("Post doesn't have comments", file=stderr)
        print("---------------", file=stderr)
    else:
      print("Post was deleted", file=stderr)
      print("---------------", file=stderr)

def run_bot(subreddit_handler):
  check_new_posts(subreddit_handler.new(limit=15))
  sleep(30)
