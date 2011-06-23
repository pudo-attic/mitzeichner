from core import Delegation
import urllib2, urllib
import cookielib
from lxml import html

LOGIN_URL = "https://epetitionen.bundestag.de/index.php?action=login2"
PETITION_URL = "https://epetitionen.bundestag.de/index.php?action=petition;sa=sign;petition=%s"

class CookieRedirectHandler(urllib2.HTTPRedirectHandler):

    def __init__(self, jar):
        self.jar = jar

    def http_error_302(self, req, fp, code, msg, headers):
        self.jar.extract_cookies(fp, req)
        result = urllib2.HTTPRedirectHandler.http_error_302(
            self, req, fp, code, msg, headers)
        result.status = code
        return result

def make_jar(username, password):
    jar = cookielib.CookieJar()
    params = urllib.urlencode(
        {'user': username, 
         'passwrd': password, 
         'hash_passwrd': ''})
    req = urllib2.Request(LOGIN_URL, params)
    req.add_header('Referer', LOGIN_URL)
    opener = urllib2.build_opener(CookieRedirectHandler(jar))
    fp = opener.open(req)
    jar.extract_cookies(fp, req)
    return jar, fp

def check_credentials(username, password):
    jar, fp = make_jar(username, password)
    if 'login' in fp.url:
        return False
    return True

def sign(username, password, petition_id):
    jar, fp = make_jar(username, password)
    req = urllib2.Request(PETITION_URL % petition_id)
    jar.add_cookie_header(req)
    fp = urllib2.urlopen(req)
    doc = html.parse(fp)
    sign_link = doc.find('//div[@class="sign_top"]/a')
    if sign_link is None:
        return False
    if 'entfernen' in sign_link.text:
        return True
    url = sign_link.get('href')
    req = urllib2.Request(url)
    jar.add_cookie_header(req)
    fp = urllib2.urlopen(req)
    fp.read()
    fp.close()
    return True

def delegations(mitzeichner):
    delegations = Delegation.by_theme_name(mitzeichner.theme,
            mitzeichner.name, mitzeichner.location)
    for delegation in delegations:
        sign(delegation.username, delegation.password, mitzeichner.petition_id)



