#!/usr/bin/python

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import getopt
import getpass
import json
import hashlib
import base64

### Non-builtin imports
try:
  import requests
except ImportError:
  pass

try:
  from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
  from cryptography.hazmat.primitives.padding import PKCS7
  from cryptography.hazmat.backends import default_backend
except ImportError:
  pass

try:
  import pyaes
except ImportError:
  pass

## Check dependency requirements
missing_msg = []
fail = False

# Need requests
if "requests" not in sys.modules:
  fail = True
  missing_msg += [ "requests" ]

# Need either cryptography or pyaes
if "cryptography" not in sys.modules and "pyaes" not in sys.modules:
  fail = True
  missing_msg += [ "cryptography or pyaes" ]

if fail == True:
  print("Error: missing dependencies.")
  print("Please install the following modules: " + ", ".join(missing_msg))
  sys.exit(1)

### Encryption functions

def encrypt_pyaes(key, iv, msg):
  """encrypt using pyaes module"""
  mode = pyaes.AESModeOfOperationCBC(key, iv=iv)
  encrypter = pyaes.blockfeeder.Encrypter(mode)
  return encrypter.feed(msg) + encrypter.feed()

def encrypt_cryptography(key, iv, msg):
  """encrypt using cryptography module"""
  padder = PKCS7(128).padder()
  msg_padded = padder.update(message.encode("utf8")) + padder.finalize()

  cipher = Cipher(algorithms.AES(key),
                  modes.CBC(iv),
                  backend=default_backend())
  encryptor = cipher.encryptor()
  return encryptor.update(msg_padded) + encryptor.finalize()

# Encrypt msg using AES in CBC mode and PKCS#7 padding, using either
# cryptography or pyaes
def encrypt(key, iv, msg):
  if "cryptography" in sys.modules:
    return encrypt_cryptography(key, iv, msg)
  elif "pyaes" in sys.modules:
    return encrypt_pyaes(key, iv, msg)

# Encrypt the password like the captive portal's Javascript does
def encrypt_password(ip, password):
    # Salt for PBKDF2
    salt = bytearray.fromhex("77232469666931323429396D656F3938574946")
    # Initialization vector for CBC
    iv = bytes(bytearray.fromhex("72c4721ae01ae0e8e84bd64ad66060c4"))
    
    # Generate key from IP address
    key = hashlib.pbkdf2_hmac("sha1", ip.encode("utf8"), salt, 100, dklen=32)
    
    # Encrypt password
    ciphertext = encrypt(key, iv, password)
    
    # Encode to Base64 (explicitly convert to string for Python 2/3 compat)
    ciphertext_b64 = base64.b64encode(ciphertext).decode("ascii")
    
    return ciphertext_b64

### Misc

# Reads a line from standard input (Python 2/3 compat)
def get_input(prompt):
  if sys.version_info < (3, 0):
    return raw_input(prompt)
  else:
    return input(prompt)

# Read a jsonp string.
def read_jsonp(jsonp):
  jsonp_stripped = jsonp[ jsonp.index("(")+1 : jsonp.rindex(")") ]
  return json.loads(jsonp_stripped)

### Main application logic

# Get the state of the connection from the server
def get_state():
  url = 'https://servicoswifi.apps.meo.pt/HotspotConnection.asmx/GetState?callback=foo&mobile=false&pagePath=foo'
  response = requests.get(url)
  state = read_jsonp(response.content.decode(response.encoding))
  return state

# Get our LAN IP address
def get_ip():
  # It's included in the connection state. That's where the web interface gets it, too.
  state = get_state()
  return state["FrammedIp"]

# Make a GET request with the required data to login to a MEO Wifi Premium Hotspot
def meo_wifi_login(username, password):
  ip = get_ip()
  encrypted_password = encrypt_password(ip, password)
  url ='https://servicoswifi.apps.meo.pt/HotspotConnection.asmx/Login?username=' + username+ '&password=' + encrypted_password + '&navigatorLang=pt&callback=foo'
  response = requests.get(url)

  return response

# Make a GET request to logoff from a MEO Wifi Premium Hotspot
def meo_wifi_logoff():
  url = 'https://servicoswifi.apps.meo.pt/HotspotConnection.asmx/Logoff?callback=foo'
  response = requests.get(url)

  return response

def main():
  # Retrieve environment variables
  user=os.getenv('MEO_WIFI_USER', '')
  passwd=os.getenv('MEO_WIFI_PASSWORD', '')

  # Parse the arguments
  opts, args = getopt.getopt(sys.argv[1:], "hxu:p:")
  for (opt, arg) in opts:
    if opt == '-h':
      print(sys.argv[0] + '-u <login user> -p <login password>')
      sys.exit()
    elif opt == '-x':
      print('Logging off...')
      print(meo_wifi_logoff())
      sys.exit()
    elif opt == '-u':
      user = arg
    elif opt == '-p':
      passwd = arg

  # Determine if user and passwords were specified (and ask for them if not)
  if not user:
    user=get_input('Introduza o e-mail Cliente MEO: ')
  if not passwd:
    passwd=getpass.getpass('Introduza a password Cliente MEO (' + user + '): ')

  # After gathering the necessary data, execute the request
  print(meo_wifi_login(user,passwd))

if __name__ == '__main__':
  main()
