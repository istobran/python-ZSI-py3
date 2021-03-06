#! /usr/bin/env python
# $Header$
'''Utilities for HTTP Digest Authentication
'''

from md5 import md5
import random
import time
import http.client

random.seed(int(time.time()*10))

def H(val):
  return md5(val).hexdigest()

def KD(secret,data):
  return H('%s:%s' % (secret,data))

def A1(username,realm,passwd,nonce=None,cnonce=None):
  if nonce and cnonce:
    return '%s:%s:%s:%s:%s' % (username,realm,passwd,nonce,cnonce)
  else:
    return '%s:%s:%s' % (username,realm,passwd)

def A2(method,uri):
  return '%s:%s' % (method,uri)

def dict_fetch(d,k,defval=None):
  if k in d:
    return d[k]
  return defval

def generate_response(chaldict,uri,username,passwd,method='GET',cnonce=None):
  """
  Generate an authorization response dictionary. chaldict should contain the digest
  challenge in dict form. Use fetch_challenge to create a chaldict from a HTTPResponse
  object like this: fetch_challenge(res.getheaders()).

  returns dict (the authdict)

  Note. Use build_authorization_arg() to turn an authdict into the final Authorization
  header value.
  """
  authdict = {} 
  qop = dict_fetch(chaldict,'qop')
  domain = dict_fetch(chaldict,'domain')
  nonce = dict_fetch(chaldict,'nonce')
  stale = dict_fetch(chaldict,'stale')
  algorithm = dict_fetch(chaldict,'algorithm','MD5')
  realm = dict_fetch(chaldict,'realm','MD5')
  opaque = dict_fetch(chaldict,'opaque')
  nc = "00000001"
  if not cnonce:
    cnonce = H(str(random.randint(0,10000000)))[:16]

  if algorithm.lower()=='md5-sess':
    a1 = A1(username,realm,passwd,nonce,cnonce)
  else:
    a1 = A1(username,realm,passwd)

  a2 = A2(method,uri)

  secret = H(a1)
  data = '%s:%s:%s:%s:%s' % (nonce,nc,cnonce,qop,H(a2))
  authdict['username'] = '"%s"' % username
  authdict['realm'] = '"%s"' % realm
  authdict['nonce'] = '"%s"' % nonce
  authdict['uri'] = '"%s"' % uri
  authdict['response'] = '"%s"' % KD(secret,data)
  authdict['qop'] = '"%s"' % qop
  authdict['nc'] = nc
  authdict['cnonce'] = '"%s"' % cnonce
  
  return authdict


def fetch_challenge(http_header):
  """
  Create a challenge dictionary from a HTTPResponse objects getheaders() method.
  """
  chaldict = {}
  vals = http_header.split(' ')
  chaldict['challenge'] = vals[0]
  for val in vals[1:]:
    try:
      a,b = val.split('=')
      b=b.replace('"','')
      b=b.replace("'",'')
      b=b.replace(",",'')
      chaldict[a.lower()] = b
    except:
      pass
  return chaldict


def build_authorization_arg(authdict):
  """
  Create an "Authorization" header value from an authdict (created by generate_response()).
  """
  vallist = []
  for k in list(authdict.keys()):
    vallist += ['%s=%s' % (k,authdict[k])]
  return 'Digest '+', '.join(vallist)

if __name__ == '__main__': print(_copyright)
