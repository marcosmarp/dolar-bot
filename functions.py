from praw import Reddit
from os import environ
from sys import stderr
from time import sleep, time
import cryptocompare
import pytz
from datetime import datetime
from requests import get
from bs4 import BeautifulSoup
from locale import setlocale, LC_ALL, format
setlocale(LC_ALL, 'es_AR')

commands = ['!dolar', '!dólar', '!cripto']

def reset_timer():
  return time()

def init_praw():
  return Reddit(
    client_id = environ['CLIENT_ID'],
    client_secret = environ['CLIENT_SECRET'],
    user_agent="console:dolar-bot:v2.0.0 (by u/dolar-bot)",
    username = "dolar-bot",
    password = environ['PASSWORD']
  )

def log_error(message):
  print(message, file=stderr)
  print("---------------", file=stderr)

def post_have_comments(post):
  return (post.num_comments > 0)

def already_replied(replies):
  for reply in replies:
    if reply.author.name == "dolar-bot":
      return True
  return False

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

def reply_comment(comment, reply):
  comment.reply(reply)
  sleep(5)

def generate_dolar_reply():
  dolar_values = get_dolar_values() 

  reply = """
  |Divisa|Compra|Venta|
  |:-|:-|:-|
  |**Oficial**|AR{0}|AR{1}|
  |**Blue**|AR{2}|AR{3}|
  |**MEP/Bolsa**|AR{4}|AR{5}|
  |**CCL**|AR{6}|AR{7}|'
  |**Solidario** (+30%)|\-|AR{8}|
  |**Tarjeta** (+64%)|\-|AR{9}|

  Información actualizada al {10} desde [dólar hoy](https://dolarhoy.com/)
  
  ^(Soy un bot y esta acción fue realizada automáticamente)
  
  ^(Feedback? Bugs?: )[^(Github)](https://github.com/marcosmarp/dolar-bot)
  """

  return reply.format(dolar_values[0], dolar_values[1], dolar_values[2], dolar_values[3], dolar_values[4], 
  dolar_values[5], dolar_values[6], dolar_values[7], dolar_values[8], dolar_values[9], 
  datetime.now(pytz.timezone('America/Argentina/Buenos_Aires')).strftime("%d/%m/%Y %H:%M:%S"))

def format_float(num):
  return format("%.2f", num, grouping=True)

def get_cripto_values():
  crypto_values = cryptocompare.get_price(['BTC', 'ETH', 'BNB', 'USDT', 'ADA', 'SOL', 'XRP', 'DOT', 'DOGE', 'SHIB' ], ['ARS'])

  return [format_float(crypto_values['BTC']['ARS']), format_float(crypto_values['ETH']['ARS']), 
  format_float(crypto_values['BNB']['ARS']), format_float(crypto_values['USDT']['ARS']), 
  format_float(crypto_values['ADA']['ARS']), format_float(crypto_values['SOL']['ARS']), 
  format_float(crypto_values['XRP']['ARS']), format_float(crypto_values['DOT']['ARS']), 
  format_float(crypto_values['DOGE']['ARS']), format_float(crypto_values['SHIB']['ARS']*1000)]

def generate_cripto_reply():
  cripto_values = get_cripto_values() 

  reply = """
  |Divisa|Ultimo valor de trading|
  |:-|:-|
  |**BTC**|AR${0}|
  |**ETH**|AR${1}|
  |**BNB**|AR${2}|
  |**USDT**|AR${3}|
  |**ADA**|AR${4}|
  |**SOL**|AR${5}|
  |**XRP**|AR${6}|
  |**DOT**|AR${7}|
  |**DOGE**|AR${8}|
  |**SHIB (x1000)**|AR${9}|

  Información actualizada al {10} desde [CryptoCompare](https://www.cryptocompare.com/coins/list/all/USD/1)
  
  ^(Soy un bot y esta acción fue realizada automáticamente)
  
  ^(Feedback? Bugs?: )[^(Github)](https://github.com/marcosmarp/dolar-bot)
  """

  return reply.format(cripto_values[0], cripto_values[1], cripto_values[2], cripto_values[3], cripto_values[4], 
  cripto_values[5], cripto_values[6], cripto_values[7], cripto_values[8], cripto_values[9],
  datetime.now(pytz.timezone('America/Argentina/Buenos_Aires')).strftime("%d/%m/%Y %H:%M:%S"))

def inform_reply_on_screen(comment):
  now = datetime.now(pytz.timezone('America/Argentina/Buenos_Aires'))
  dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
  print("           " + dt_string + ": replied " + comment.author.name + "'s comment", file=stderr)
  print("---------------", file=stderr)

def check_for_command(comment):
  for command in commands:
    if command in comment.body.lower():
      return True
  return False

def get_command(comment):
  for command in commands:
    if command in comment.body.lower():
      return command

def check_comments(comments):
  for comment in comments:
      if hasattr(comment, "replies"):
        check_comments(comment.replies)

      if not hasattr(comment, "body"):
        log_error("Empty comment")
        continue
      print("   Comment have body", file=stderr)

      if comment.author is None:
        log_error("Comment deleted")
        continue
      print("   Checking " + comment.author.name + "'s comment", file=stderr)

      if not check_for_command(comment):
        log_error("Comment doesn't mentions a command'")
        continue
      command = get_command(comment)
      print("       Comment mentions " + command, file=stderr)

      if already_replied(comment.replies):
        log_error("Comment already replied")
        continue
      print("         Comment yet to be replied", file=stderr)

      if command == "!dolar" or command == "!dólar":
        reply_comment(comment, generate_dolar_reply())
      elif command == "!cripto":
        reply_comment(comment, generate_cripto_reply())    
      inform_reply_on_screen(comment)

      return

def check_new_posts(posts):
  for post in posts:
    if post.author is None:
      log_error("Post deleted")
      continue
    print("Checking " + post.author.name + "'s '" + post.title + "' post", file=stderr)

    if not post_have_comments(post):
      log_error("Post doesn't have comments")
      continue
    print(" Post have comments", file=stderr)

    check_comments(post.comments)

def run_bot(subreddit_handler):
  check_new_posts(subreddit_handler.new(limit=15))
  sleep(30)
