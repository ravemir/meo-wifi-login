#!/usr/bin/python

import os
import sys
import getopt
import getpass

import requests
import json


# Sends a POST request with the required data to login to a MEO Wifi Premium Hotspot
def meo_wifi_login(username, password):
  url ='https://servicoswifi.apps.meo.pt/HotspotConnection.asmx/Login?username=' + username+ '&password=' + password + '&navigatorLang=pt&callback=foo'
  response = requests.get(url)

  return response

# Sends a POST request to logoff from a MEO Wifi Premium Hotspot
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
      print sys.argv[0] + '-u <login user> -p <login password>'
      sys.exit()
    elif opt == '-x':
      print 'Logging off...'
      print meo_wifi_logoff()
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
