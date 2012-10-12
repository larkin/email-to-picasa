""" 
utils.py

declares process_email, a utility function 
that uploads attachments to picasa albums
"""

from google.appengine.ext import blobstore
from application.models import UnprocessedEmail, AlbumEmailMapping, \
                               UserCredential
import httplib2
import logging

def process_email(emailid):
    #get email   
    email = UnprocessedEmail.get_by_id(emailid)
    email_key = email.to_address.split('@')[0]
    # find mapping
    mapping = AlbumEmailMapping.all().filter('email_address =', email_key) \
                               .get()
    if not mapping:
        logging.info('mapping not found: %s' % email_key)
        return

    # get credential
    credential = UserCredential.get_by_user(mapping.owner)
    if not credential:
        logging.info('No credential found for user %s, cannot upload.' 
                     % mapping.owner)
        return

    # gotta grab url. check links on album data
    url = None
    for link in mapping.album['link']:
      if link['rel'] == 'http://schemas.google.com/g/2005#feed':
        url = link['href'].split('?alt')[0]
    
    if not url:
        logging.info('couldn\'t find feed url')
        return

    logging.info('here\s my uri!: %s' % url)

    h = httplib2.Http()
    h = credential.authorize(h)
    for key in email.attachment_keys:
        blobinfo = blobstore.BlobInfo.get(key)
        value = blobstore.BlobReader(blobinfo).read()
        response = h.request(url, method="POST", 
                       headers={
                           'Content-Type': blobinfo.content_type, 
                           'Content-Length': str(blobinfo.size)}, 
                       body=value)
                   
        logging.info('posted some shit, see the response:')
        logging.info(response)
    
    UserCredential.set_credentials_for_user(mapping.owner, credential)

    # clean up
    blobinfo.delete()
    email.delete()