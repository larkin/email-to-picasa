""" inbound mail handler and processors """
from __future__ import with_statement

import logging

from google.appengine.ext import webapp 
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler 
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.deferred import defer
from google.appengine.api import files

from application.utils import process_email

from application.models import UnprocessedEmail

class HandleInboundEmail(InboundMailHandler):
    def receive(self, message):
        logging.info("received email from %s, sent to %s, actual address: %s" 
                     % (message.sender, message.to, self.request.path[10:]))
        # check for attachments
        if not hasattr(message, 'attachments'):
            logging.info("message does not have attachments " + 
                         "nothing to do here.")
            return
            
        # to_address could be masked, so get from handler.
        to_address = self.request.path[10:]
        attachment_keys = []
        for f_name, f_contents in message.attachments:
            # determine mime type
            extension = f_name.split('.')[-1].lower()
            mime_type = None
            if extension in ['jpg', 'jpeg']:
                mime_type = 'image/jpeg'
            elif extension == 'png':
                mime_type = 'image/png'
            elif extension == 'gif':
                mime_type = 'image/gif'
            elif extension == 'bmp':
                mime_type = 'image/bmp'
            
            if not mime_type:
                continue # file type not recognized
                
            file_name = files.blobstore.create(mime_type=mime_type)
            with files.open(file_name, 'a') as f:
                f.write(f_contents.decode())
                
            files.finalize(file_name)
            
            attachment_keys.append(files.blobstore.get_blob_key(file_name))
            
        unprocessed_email = UnprocessedEmail(to_address=to_address, 
                                             attachment_keys=attachment_keys)
        unprocessed_email.put()
        logging.info('stashed new unprocessed email id %s with %s attachments' 
                     % (unprocessed_email.key().id(), len(attachment_keys)))
        defer(process_email, unprocessed_email.key().id())

inbound_handler = webapp.WSGIApplication([HandleInboundEmail.mapping()], debug=False)