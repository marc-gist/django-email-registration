=========================
django-email-registration
=========================

The eleventy-eleventh email registration app for Django.

But this one does not feed your cat.

Original: https://github.com/matthiask/django-email-registration
Thanks!

Changes
=======

1.  Mostly changed so that we have no ajax calls, setup bcc, and reset password
    ability.

Usage
=====

This example assumes you are using a recent version of Django, jQuery and
Twitter Bootstrap.

1. Install ``django-email-registration`` into your django installed apps
    note: to keep this seperate from my usual app, I just ln -s the application directory
    into my main application (keeps git seperate)

2. include:
   ``registration/email_registration_include.html`` somewhere.)

3. Add ``email_registration`` to ``INSTALLED_APPS`` and include
   ``email_registration.urls`` somewhere in your URLconf.

4. Make sure that EMAIL_ options in settings.py are defined
   I.e. EMAIL_HOST = smtp.server.provider.com, EMAIL_PORT = 587, E
   MAIL_HOST_USER = , EMAIL_HOST_PASSWORD
