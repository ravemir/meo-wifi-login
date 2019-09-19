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
import urllib
if sys.version_info >= (3, 0):
  import urllib.request
  urllib = urllib.request

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
  msg_padded = padder.update(msg.encode("utf8")) + padder.finalize()

  cipher = Cipher(algorithms.AES(key),
                  modes.CBC(iv),
                  backend=default_backend())
  encryptor = cipher.encryptor()
  return encryptor.update(msg_padded) + encryptor.finalize()

def encrypt(key, iv, msg):
  """Encrypt msg using AES in CBC mode and PKCS#7 padding.

  Will use either the cryptography or pyaes module, whichever is
  available.

  """
  if "cryptography" in sys.modules:
    return encrypt_cryptography(key, iv, msg)
  elif "pyaes" in sys.modules:
    return encrypt_pyaes(key, iv, msg)

def encrypt_password(ip, password):
  """Encrypt the password like the captive portal's Javascript does"""
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
  
  return urllib.quote(ciphertext_b64)

### Misc

def get_input(prompt):
  """Reads a line from standard input (Python 2/3 compat)"""
  if sys.version_info < (3, 0):
    return raw_input(prompt)
  else:
    return input(prompt)

def read_jsonp(jsonp):
  """Read a jsonp string."""
  jsonp_stripped = jsonp[ jsonp.index("(")+1 : jsonp.rindex(")") ]
  return json.loads(jsonp_stripped)

### Networking

class UrlOpen:
  """Wrapper around urllib for http requests."""
  
  def __init__(self, url, maxsize=2**20):
    """Makes the request and reads up to maxsize bytes from the response."""
    conn = urllib.urlopen(url)
    code = conn.getcode()
    data = b''
    while len(data) <= maxsize:
      buf = conn.read(maxsize-len(data))
      data += buf
      if len(buf) == 0:
        break
    conn.close()
    self.conn = conn
    self.code = code
    self.rawdata = data
  
  @property
  def text(self):
    """Decoded response data"""
    # TODO: Get the right character encoding from the response headers.
    return self.rawdata.decode("utf-8")
  
  @property
  def response(self):
    """Human-readable representation of response code"""
    # TODO: improve
    if (self.code == 200):
      return "OK"
    else:
      return "Unexpected response. Code: " + self.code

def get_url_text(url):
  """Get url and return the decoded response data."""
  # Use 'requests' by default and urllib as fallback
  if "requests" in sys.modules:
    response = requests.get(url)
    return response.content.decode(response.encoding)
  else:
    return UrlOpen(url).text

def get_url_result(url):
  """Get url and return the response code"""
  # Use 'requests' by default and urllib as fallback
  if "requests" in sys.modules:
    return requests.get(url)
  else:
    return UrlOpen(url).response

### Main application logic

def get_state():
  """Get the state of the connection from the server"""
  url = 'https://servicoswifi.apps.meo.pt/HotspotConnection.asmx/GetState?callback=foo&mobile=false&pagePath=foo'
  state = read_jsonp(get_url_text(url))
  return state

def get_ip(state=None):
  """Get our LAN IP address"""
  if state is None:
    state = get_state()
  return state["FrammedIp"]

def meo_wifi_login(username, password):
  """Make a GET request with the required data to login to a MEO Wifi Premium Hotspot"""
  ip = get_ip()
  if ip is None:
    print("Error: failed to determine IP address.\nPlease verify that you are connected to a MEO WiFi network.")
    sys.exit(1)

  encrypted_password = encrypt_password(ip, password)
  url ='https://servicoswifi.apps.meo.pt/HotspotConnection.asmx/Login?username=' + username+ '&password=' + encrypted_password + '&navigatorLang=pt&callback=foo'
  response = get_url_result(url)

  return response

def meo_wifi_logoff():
  """Make a GET request to logoff from a MEO Wifi Premium Hotspot"""
  url = 'https://servicoswifi.apps.meo.pt/HotspotConnection.asmx/Logoff?callback=foo'
  response = get_url_result(url)

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
