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
Oh boy, not sure here.  The dependencies are included in this repo 
because in order to upload it to app engine, you'd need to do that.  But 
there are more things that need to be set up.  Here's an incomplete list:

1. you'll need to create a `secret_keys.py` file declaring two strings,
`CSRF_SECRET_KEY` and `SESSION_KEY`.  This file should be located at 
`application/secret_keys.py`
2. you'll need to generate and download a `client-secrets.json` file in
order to access the google apis.
3. you'll need to change app.yaml and email address associated with the app.

# thanks to

* [flask](http://flask.pocoo.org)
* [werkzeug](http://werkzeug.pocoo.org/)
* [google-api-python-client](https://code.google.com/p/google-api-python-client/)

Did I miss your contribution?  I deeply apologize; please let me know and I'll 
update this list immediately.

[Pete Richards](http://www.pete-richards.com)
