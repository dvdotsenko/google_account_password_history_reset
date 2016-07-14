Selenium-based Google account password history clearing script

Wanted to use one of previously-used passwords with a Google account,
but Google remembers last 100 uses passwords and does not allow reuse of them.

This script will flush out the password history by changing the password enough
times to push all previously-used passwords from history.

Found these but it's for Windows only (and for very old version of Google site), which
does not work for me:

http://roozbeh-eng.blogspot.com/2013/04/an-updated-script-to-change-your-gmail.html
https://gist.github.com/bjarki/9886887


In order to run this, you need Selenium's Python bindings and ChromeDriver for Selenium.

ChromeDriver:
https://sites.google.com/a/chromium.org/chromedriver/downloads
(update CHROMEDRIVER_BINARY_PATH value below)

Selenium Python bindings:
`virtualenv .venv/`
`source .venv/bin/activate`
`pip install -r requirements.txt`

Run:
Make sure to set several password recovery options before you run this.

`python main.py 'my.email@gmail.com' 'current password' 'desired password'`
