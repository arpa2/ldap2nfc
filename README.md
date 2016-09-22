# Making LDAP information available over NFC

> *Download contact information from their primary online location, and
> map them via vCard fomat to NDEF.  NDEF is the NFC payload.  NDEF can be
> flashed onto electronic business cards, or downloaded into smart phones.*

(Future tools in this package may achieve more mappings from LDAP to NFC,
just sit and watch... or send us your additions!)

This idea involves a number of technologies, making the best of each:

  * **LDAP** is an online database that anyone can run under their own
    domain name; it can be sought in a standard way, namely by zooming
    in on the domain and then searching for a userid.  The data found
    there can be descriptive of a person, and it is described in a
    properly standardised format.  Meaning, you can fully automate these
    downloads.
  * **vCard** is a common used representation for *fixed* contact info.
    This means it can be used to transport such data, but in real fact
    it is probably better to query LDAP once in a while to get an update.
  * **NDEF** is the format used for Near Field Communication, common on
    a growing number of mobile devices.

You can use this in a number of ways.

## Electronic Business Cards

You can create an electronic business card from an NFC Tag.  To do this,
use your favourite tool to upload the NDEF output into your NFC Tag.
These can take various shapes: plastic cards, key tags, stickers.  Count
on $0.20 to $2.00 for each.  In September 2016, NFC Tags tend to go up
to 888 bytes of user data, most of which can be filled with NDEF data.

Anyone with a phone capable of using NFC can swipe the tag and extract
the business card contents electronically.  This applies to Android,
Blackberry and Windows phones.  Upcoming iPhones and iPads will also
support NFC, but its functionality will be crippled by a vendor who
wants to control it as a payment instrument; if you think this is bad,
then you may want to let them know that this is why your next phone will
be Android.

This is done with the following command:

    ldap2vcard2ndef.py john.doe@example.com

This assumes an LDAP server for `example.com`, found DNS SRV records like

    _ldap._tcp  IN SRV  389 10 10  ldap.example.com.

and after connecting anonymously, this makes a search under

    dc=example,dc=com

with the object filter

   (&(objectClass=person)(uid=john.doe))

and if it finds exactly one, it will map LDAP attributes to their vCard form,
which is then packed into an NDEF file.  You can use your favourite NFC tools
to pass the NDEF file, through your NFC Reader/Writer, to your NFC Tag that
will act as a business card.

### Special use case: Event-specific Contact Details

Although `john.doe@example.com` is likely to have a hefty spam filter on his
mailbox, he may want to give a temporary window of access to visitors of an
event that he is also visiting.  To that end, he could create a short-lasting
alias such as `john.doe+sha2017@example.com` and ship those temporary details
to his NFC Tag.  Even when the address printed on the front is still the same
old spam-filtered address, he might give a different level of access to the
temporary mailbox for those who scanned it.

## Downloading or Updating your Contact Database

You can use this utility to download your contacts and place them into one
large NDEF file.  Then you tap your NFC Reader/Writer with your phone and
it will download the new information for you.  If the receiving-end software
is clever enough it will replace the prior vCards with the new ones.

To do this sort of thing, simply call the tool with multiple addresses.

TODO: NFC Reader/Writer awaits NFC uploads, retrieves originating
LDAP URI from each vCard and retrieves updated information; lacking a
direct LDAP URI it could derive one from an email address or similar
form; and writes it back as an update inasfar as vCards have changed.


## Programming API

The script can run as a main program, or as a library.  See the main
program for the rather trivial mapping; essentially, the invocations
given above can be turned into a function call to `ldap2vcard2ndef.lookup()`
with the same parameters.

Future versions may include options, the defaults of which will match
with the expected behaviour.  Presentation of options will map to
keyword arguments that match the long option name.


## Requirements

This script uses the following Python components:

  * [python-ldap](https://pypi.python.org/pypi/python-ldap)
    for accessing LDAP clients written in Python;
  * [srvlookup](https://pypi.python.org/pypi/srvlookup)
    for locating the LDAP server;
  * [ndeflib](https://pypi.python.org/pypi/ndeflib)
    for constructing the NDEF file.

You may want to combine it with

  * [nfcpy](https://pypi.python.org/pypi/nfcpy)
    for accessing your NFC Reader/Writer from Python.


## Thanks

Many thinks to the people who constructed the required and usefully
combining underlying packages.

While making this script, I gleaned at the Python script
[LDAP2VCard.py](https://github.com/mkiol/LDAP2VCard/blob/master/LDAP2VCard.py)
by
[Mkiol](https://github.com/mkiol)
as a reminder of how things are done with Python-LDAP.

