# Making LDAP information available over NFC

> *Download contact information from your contacts' LDAP database, and
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

Creating the content for your business card is done with:

    ldap2ndef.py john.doe@example.com

The output will be written to the file `output.ndef`, ready for your
favourite NFC Reader/Writer to pass it on.

This assumes an LDAP server for `example.com`, announced in DNS SRV records like

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

The `ldap2ndef` script can run as a main program, or as a library.  See the
main program for the rather trivial mapping; essentially, the invocations
given above can be turned into a function call to `ldap2ndef.lookup()`
with the same parameters.

Future versions may include options, the defaults of which will match
with the expected behaviour.  Presentation of options will map to
keyword arguments that match the long option name.

Briefly put, you could:

    import ldap2ndef
    ndefobj = ldap2ndef.lookup ('john.doe@example.com', 'jane.doe@example.net')


## Global Directory

This code assumes the LDAP global directory, which is nothing more than a
definition of a DNS SRV record for LDAP under participating domain names:

    _ldap._tcp.example.com.  IN SRV  389 10 10  ldap.example.com.

The information published here can be public (meaning, available after
binding anonymously) or it can be private (meaning, it requires actual
login during the binding phase).  It is normal for LDAP servers to provide
a variety of choices when it comes to visibility of objects and attributes.

The `ldap2nfc` utility currently extracts public information, which covers
the usecase of pulling information for a contact based on their email
address.  The other usecase, namely to pull your own contact information
to a business card, might require more openness and therefore need you to
login.  That is not currently implemented, since this is merely intended
for demonstration purposes right now.

There is a lot of potential in this distributed, locally controlled form
of data, especially because both the protocol and data types are rather
well standardised, and yet they are easily extensible!  To read more about
the potential of a Global Directory, proceed to our
[technical exploration](http://rickywiki.vanrein.org/doku.php?id=globaldir).


## IdentityHub

This project is an early demonstration of the Identity Hub, or second phase
of the InternetWide.org project, which aims to improve decentralisation
and self-control of online presence by putting up an architecture into which
we can hang the plethora of individual open source projects that are now
being created.

[Read more about the project](http://internetwide.org/blog/2016/06/24/iwo-phases.html)


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

