# meo-wifi-login

## Description:
Allows for an automated login through a MEO Wifi Premium hotspot.

## Usage
You may use `meo_wifi_login.py` file as regular script, running it via CLI...:

```
./meo_wifi_login -u <username> -p <password>
```

...or call the `meo_wifi_login` function through your script:
```
import meo_wifi_login

meo_wifi_login.meo_wifi_login('user','pass')
```

The script also looks for a `MEO_WIFI_USER` and `MEO_WIFI_PASSWORD` environment variable for the login information.

In case neither of these sources are available, it will prompt the user via console to fill them

Starting July 2024, a new login portal was observed across some routers, hosted under "meowifi.meo.pt" and the script was adapted to its login method.
The old login method, targetting "servicoswifi.apps.meo.pt" is still available through the legacy ('-l') option, for both login and logout operations.

## Dependencies
Beyond the standard Python libraries, you may need to install the following:

- `requests` *(optional, recommended)*
- `cryptography` *OR* `pyaes` *(only required when using the legacy option)*

You can install them using pip. For example:

```
pip install requests cryptography
```

Several Linux distros also have packages for them. For example, in Debian 10 you can install them like this:

```
sudo apt-get install python-requests python-cryptography
```


### Notes
- `requests` is used to make HTTPS requests. A working (but probably less robust) urllib-based fallback is included.
- `cryptography` and `pyaes` are used to encrypt the password using AES.
- `cryptography` is preferred and more likely to already be installed or available in distributions.
- `pyaes` is a pure python alternative to `cryptography` and is good to have for when `cryptography` is harder to install. (e.g. Termux)
- The code has been ported to work on both Python 2 and 3. Make sure you install your dependencies for the version of Python you will be running the script with.

#### Python < 2.7.9
Python earlier than 2.7.9 has some restrictions on their `ssl` module that limits the configuration `urllib3` can apply.

If you have a `InsecurePlatformWarning` error, update Python to v2.7.9+ or install `requests` extra package set `security` with:


```
pip install requests[security]
```

This should install the following extra packages:

* pyOpenSSL>
* ndg-httpsclient
* pyasn1








