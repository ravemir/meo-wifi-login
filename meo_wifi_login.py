#!/usr/bin/python
import os
import sys
import getopt
import getpass

from mechanize import Browser
import urllib


# Creates a POST request with the required data to login to a MEO Wifi Premium Hotspot
def meo_wifi_login(username, password):
  br = Browser()
  url ='https://wifi.meo.pt/HttpHandlers/HotspotConnection.asmx/Login?usr=' + username
  data = urllib.urlencode({
              'username': username,
              'password': password })
  response = br.open(url,data).read()
  return response

def meo_wifi_logoff():
  br = Browser()
  url = 'https://wifi.meo.pt/HttpHandlers/HotspotConnection.asmx/Logoff'
  response = br.open(url,data).read()
  return response

def main():
  # Retrieve environment variables
  user=os.getenv('MEO_WIFI_USER', '')
  passwd=os.getenv('MEO_WIFI_PASSWORD', '')

  # Parse the arguments
  opts, args = getopt.getopt(sys.argv[1:], "hu:p:")
  for (opt, arg) in opts:
    if opt == '-h':
      print sys.argv[0] + '-u <login user> -p <login password>'
      sys.exit()
    elif opt == '-u':
      user = arg
    elif opt == '-p':
      passwd = arg

  # Determine if user and passwords were specified (and ask for them if not)
  if not user:
    user=raw_input('Introduza o e-mail Cliente MEO: ')
  if not passwd:
    passwd=getpass.getpass('Introduza a password Cliente MEO (' + user + '): ')

  # After gathering the necessary data, execute the request
  print meo_wifi_login(user,passwd)

if __name__ == '__main__':
  main()
