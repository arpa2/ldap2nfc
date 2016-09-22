#!/usr/bin/python
#
# ldap2ndef.py -- Python package, also callable as a main program.
#
# Download contact information from their primary online location, and
# map them via vCard fomat to NDEF.  NDEF can be flashed onto electronic
# business cards, or you can easily download them into your smart phone.
#
# From: Rick van Rein <rick@openfortress.nl>


import ndef
import ldap
import srvlookup


# A list of LDAP attribute names that are usable for vCard formation for NFC
_attrs = [ 'sn', 'givenName', 'displayName',
	'mail', 'telephoneNumber', 'mobile' ]

# The uid-parameterised search filter used to locate a person in LDAP
#TODO# Future versions may represent groups, companies, roles, ... in vCards
#TODO# _filter = '(&(objectClass=person)(uid=%s))'
_filter = '(&(uid=%s))'


def _find (nai):
	"""Given a NAI, lookup DNS SRV and construct coordinates, which
           are tuples of the form (url, base, filter)
	"""
	coords = []
	#TODO# Syntax validation on user and domain fields
	(user,domain) = nai.rsplit ('@', 1)
	for rr in srvlookup.lookup ('ldap', domain=domain):
		#TODO# URL escaping
		urlport = ':' + str (rr.port) if rr.port != 389 else ''
		url = 'ldap://' + rr.host + urlport + '/'
		base = ''
		for label in domain.split ('.'):
			if base != '':
				base = base + ','
			base = base + 'dc=' + label
		coord = ( url, base, _filter % user )
		coords.append (coord)
	if coords == []:
		raise Exception ('No entry for ' + domain + ' in the LDAP Global Directory')
	return coords

def _fetch (url, base, filter):
	"""Based on the given LDAP URL, lookup the user, assure it has just
	   one object representing it, and return that.  In case of problems,
	   raise an Exception.
	"""
	db = ldap.initialize (url)
	db.simple_bind_s ()
	res = db.search (base, ldap.SCOPE_SUBTREE, filter, _attrs)
	type, data = db.result (res, all=1)
	if len (data) == 0:
		raise Exception ('No such person')
	if len (data) != 1:
		pass #TODO# raise Exception ('Ambiguous personal data')
	dn, retval = data [0]
	db.unbind_s ()
	return retval

def _format (coords, sn=None, givenName=None, displayName=None, title=None, mail=None, tel=None, mobile=None):
	"""Given a dictionary of LDAP attributes found, format a vCard
	   and return its textual form.
	"""
	#TODO# Escape special characters such as \r, \n and perhaps ; and :
	retval = 'BEGIN:VCARD\r\n'
	retval = retval + 'VERSION:3.0\r\n'
	retval = retval + 'KIND:INDIVIDUAL\r\n'
	retval = retval + 'CLASS:PUBLIC\r\n'   # Found in public LDAP, after all
	#TODO# UID (from entryUUID)
	#TODO# REV (from LDAP's metadata, last changed value for the object)
	if title is not None:
		retval = retval + 'TITLE;CHARSET=UTF-8:' + title + '\r\n'
	if displayName is not None:
		retval = retval + 'FN;CHARSET=UTF-8:' + displayName + '\r\n'
	elif sn is not None and givenName is not None:
		retval = retval + 'FN;CHARSET=UTF-8:' + sn + ' ' + givenName + '\r\n'
	if mail is not None:
		retval = retval + 'EMAIL;INTERNET:' + mail + '\r\n'
	if tel is not None:
		retval = retval + 'TEL;WORK;VOICE:' + tel + '\r\n'
	if mobile is not None:
		retval = retval + 'TEL;CELL;VOICE:' + mobile + '\r\n'
	#TODO# LANG (from language descriptions in LDAP ...?)
	#TODO# ORG (from organisation)
	#TODO# LOGO (has no LDAP relative, but would be a URL)
	#TODO# ROLE (from ...)
	#TODO# RELATED,IMPP,URL (from labeledURI, and can we use the description?)
	#TODO# ADR (from address info in LDAP...)
	#TODO# GEO (from geoloc info in LDAP...?)
	#TODO# NOTE (from description)
	#TODO# MEMBER (from member's entryUUID?!? nah...)
	#TODO#
	for (url,base,filter) in coords:
		retval = retval + 'SOURCE:' + url + '\r\n'
	retval = retval + 'PRODID:ARPA2:LDAP2NFC\r\n'
	retval = retval + 'END:VCARD\r\n'
	return retval


def _records (vcard, coords, first=True, last=True):
	"""Return NDEF records for the given vCard and LDAP URLs.
	   When first and last are both True, as is the default, the result
	   can be used as a complete NDEF object.  Needless to say that if
	   this call produces multiple records, then it will only mark the
	   first with the given first flag, and only the last with the
	   given last flag.  TODO: How to tell this to ndef.encoder?
	"""
	payloads = [ ndef.Record (type='text/vcard', data=vcard) ]
	for (url,base,filter) in coords:
		payloads.append ( ndef.Record (type='urn:nfc:wkt:U', data=url) )
	#TODO# Encode first, last... how?
	retval = b''.join (ndef.message_encoder (payloads))
	return retval


#
# Main API routine
#

def lookup (*nais):
	"""Given any number of NAIs, lookup their data and format as a vCard;
	   combine entries in an NDEF file.
	"""
	retval = ''
	todo = len (nais)
	for i in range (todo):
		(first,last) = (i==0, i+1==todo)
		coords = _find (nais [i])
		found = False
		for coord in coords:
			try:
				attrs = _fetch (*coord)
				found = True
				break
			except:
				pass
		if not found:
			raise Exception ('All LDAP servers for ' + nais [i] + ' failed')
		vcard = _format (coords, **attrs)
		retval = retval + _records (vcard, coords, first, last)
	return retval


#
# Main program -- pickup any options, and make the main API call to lookup()
#

if __name__ == '__main__':
	import sys
	args = sys.argv [1:]
	if len (args) > 0 and args [0] [:1] == '-':
		while len (args) > 0 and args [0] [:2] != '--':
			args = args [1:]
	if len (args) < 1:
		sys.stderr.write ('Usage: ' + sys.argv [0] + '[options] [--] user@domain...\n')
		sys.stderr.write ('       There are no options at this time\n')
		sys.stderr.write ('       Output will be written to "output.ndef"\n')
		sys.exit (1)
	ndef = lookup (*args)
	outfile = open ('output.ndef', 'w')
	outfile.write (ndef)
	outfile.close ()

