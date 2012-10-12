import pickle
import httplib2
import json
import logging

from google.appengine.ext import db
from google.appengine.api import memcache

# URL for the user's album list.
ALBUM_LIST_URL = \
    'https://picasaweb.google.com/data/feed/api/user/default?alt=json'

# Use this property to store objects.
class ObjectProperty(db.BlobProperty):
	def validate(self, value):
		try:
			result = pickle.dumps(value)
			return value
		except pickle.PicklingError, e:
			return super(ObjectProperty, self).validate(value)

	def get_value_for_datastore(self, model_instance):
		result = super(ObjectProperty, self) \
		         .get_value_for_datastore(model_instance)
		result = pickle.dumps(result)
		return db.Blob(result)

	def make_value_from_datastore(self, value):
		try:
			value = pickle.loads(str(value))
		except:
			pass
		return super(ObjectProperty, self).make_value_from_datastore(value)

class UnprocessedEmail(db.Model):
    to_address = db.StringProperty(required=True)
    attachment_keys = ObjectProperty(required=True)

class AlbumEmailMapping(db.Model):
    owner = db.UserProperty(required=True)
    album = ObjectProperty(required=True)
    email_address = db.StringProperty(required=True)
    
class UserCredential(db.Model):
    owner_id = db.StringProperty(required=True)
    credentials = ObjectProperty(required=True)
    
    @classmethod
    def delete_by_user(self, user):
        """Deletes credentials from memcache and from datastore."""
        memcache.delete('credentials:%s' % user.user_id())
        uc = self.all().filter('owner_id =', user.user_id()).get()
        if uc:
            uc.delete()
            
    @classmethod
    def get_by_user(self, user):
        """Attempts to get user credentials.  Checks cache, then datastore.
        returns None if cannot find credentials for user."""
        credentials = memcache.get('credentials:%s' % user.user_id())
        if not credentials:
            uc = self.all().filter('owner_id =', user.user_id()).get()
            if not uc:
                return None
            
            credentials = uc.credentials
            memcache.set('credentials:%s' % user.user_id(), credentials)

        return credentials
        
    @classmethod 
    def set_credentials_for_user(self, user, credentials):
        """Updates the users credentials in both the datastore and the 
        memcache."""
        memcache.set('credentials:%s' % user.user_id(), credentials)
        uc = self.all().filter('owner_id =', user.user_id()).get()
        if not uc:
            uc = UserCredential(owner_id=user.user_id(), 
                                credentials=credentials)
        uc.put()
    
class AlbumList(object):
    # Used only to namespace some commands.
    @classmethod
    def get_for_user(self, user):
        album_list = memcache.get('album_list:%s' % user.user_id())
        if album_list:
            logging.info('found album list in memcache')
            return album_list
            
        # no album list? then we need to fetch one!
        credentials = UserCredential.get_by_user(user)
        if not credentials:
            # no credentials? No album list!
            logging.info('did not find credentials')
            return None
        
        h = httplib2.Http()
        h = credentials.authorize(h)
        
        json_data = h.request(ALBUM_LIST_URL)
        # stash the credential because it may have been refreshed (?)
        UserCredential.set_credentials_for_user(user, credentials)
        results = json.loads(json_data[1])
        
        if 'feed' not in results:
            logging.info('feed not found in results')
            return None
            
        if 'entry' not in results['feed']:
            logging.info('entry not found in feed.')
            return None
            
        album_list = results['feed']['entry']
        logging.info('new album list fetched, has %s entries' % 
                     len(album_list))
        memcache.set('album_list:%s' % user.user_id(), album_list)
        return album_list
        
    @classmethod
    def delete_for_user(self, user):
        memcache.delete('album_list:%s' % user.user_id())
    