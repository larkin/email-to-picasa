# Email-to-Picasa

A simple app that allows an authenticated user to create an email address 
and map it to a Picasa album.  From then on, all pictures sent to that email 
address are uploaded to the specified album.

This app is currently running on google app engine, and can be accessed at:
http://email-to-picasa.appspot.com

# Why?

Picasa has this feature built in, so you may be wondering why I made this.
This is slightly different: Picasa doesn't allow you to map an email directly
to an album-- it uses the subject line of the email to map photos to albums.

I wanted to all images sent to a mailing list in one album, and thus this app
was born.  It's delightful! (Okay, it's useful, but maybe not delightful)

# install notes

1. you'll need to create a `secret_keys.py` file declaring two strings,
`CSRF_SECRET_KEY` and `SESSION_KEY`.  This file should be located at 
`application/secret_keys.py`  See kamalgill/flask-appengine-template for one
method of generating this file.
2. you'll need to generate and download a `client-secrets.json` file in
order to access the google apis.
3. you'll need to change the application id in app.yaml and also change the email address
displayed in templates.
4. copy flask and werkzeug to the project directory (required for app engine)
5. follow instructions on 
[this page](https://developers.google.com/api-client-library/python/platforms/google_app_engine)
 for installing the google-api-python-client in your project directory.

# thanks to (and dependent on)

* [flask](http://flask.pocoo.org)
* [werkzeug](http://werkzeug.pocoo.org/)
* [google-api-python-client](https://code.google.com/p/google-api-python-client/)
* many mentors and friends, google.com, and the interwebs in general.

[Pete Richards](http://www.pete-richards.com)
