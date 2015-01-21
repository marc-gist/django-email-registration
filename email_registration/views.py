from smtplib import SMTPException
from django import forms
from django.contrib import messages
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from django.forms.util import ErrorList
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext as _, ugettext_lazy
from django.views.decorators.http import require_POST
from django.conf import settings
from google_recaptacha_v2 import recaptcha

from email_registration.signals import password_set
from email_registration.utils import (
    InvalidCode, decode, send_registration_mail)


class RegistrationForm(forms.Form):
    email = forms.EmailField(
        label=ugettext_lazy('email address'),
        max_length=75,
        widget=forms.TextInput(attrs={
            'placeholder': ugettext_lazy('email address'),
        }),
    )
    resetpw = forms.BooleanField(label=u'Rest password?', required=False)
    userexists = False

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            self.userexists = True
            raise forms.ValidationError(_(
                'This email address already exists as an account.'
                ' Did you want to reset your password?'))
        return email

    # def clean(self):
    #     return self.cleaned_data


@require_POST
def email_registration_form(request, form_class=RegistrationForm):

    form = form_class(request.POST)

    if hasattr(settings, 'RECAPTCHA') and settings.RECAPTCHA and settings.RECAPTCHA_KEY:
        recapptcah_response = recaptcha.submit(
            settings.RECAPTCHA_KEY,
            request.POST.get('g-recaptcha-response'),
            request.META.get("REMOTE_ADDR"))
        if not recapptcah_response.is_valid:
            messages.error(request, 'Invalid reCAPTCHA - are you a robot? %s' % recapptcah_response.get_error())
            return redirect('/')

    if form.is_valid():
        email = form.cleaned_data['email']

        try:
            send_registration_mail(email, request, from_email=settings.EMAIL_FROM, bcc=[settings.EMAIL_FROM])
            return render(request, 'registration/email_registration_sent.html', {
                'email': email,
            })
        except SMTPException:
            #return HttpResponse('Error - Unable to Send Email - please check your address and try again')
            #raise forms.ValidationError(_('Unable to Send Email - Please check your address and try again'))
            error = form._errors.setdefault('email', ErrorList())
            error.append(u'Unable to Send Email - Please check your address and try again')
    else:
        #lets look at sending a reset user
        if form.userexists and form['resetpw'].value():
            email = form['email'].value()
            try:
                user = User.objects.get(email=email)
                """:type user: User"""
                if user.is_active:
                    send_registration_mail(email, request, user=user, from_email=settings.EMAIL_FROM, bcc=[settings.EMAIL_FROM])
                    return render(request, 'registration/email_registration_sent.html', {
                        'email': email,
                    })
                else:
                    messages.error(request, 'Error trying to reset password; please contact us.')
                    return redirect('/')
            except SMTPException:
                #return HttpResponse('Error - Unable to Send Email - please check your address and try again')
                #raise forms.ValidationError(_('Unable to Send Email - Please check your address and try again'))
                error = form._errors.setdefault('email', ErrorList())
                error.append(u'Unable to Send Email - Please check your address and try again')
            except User.DoesNotExist:
                pass

    return render(request, 'register.html', {
        'form': form,
    })


def email_registration_confirm(request, code, max_age=3 * 86400):
    try:
        email, user = decode(code, max_age=max_age)
    except InvalidCode as exc:
        messages.error(request, '%s' % exc)
        return redirect('/')

    if not user:
        if User.objects.filter(email=email).exists():
            messages.error(request, _(
                'This email address already exists as an account.'
                ' Did you want to reset your password?'))
            return redirect('/')

        user = User(
            # username=email if len(email) <= 30 else get_random_string(10)+"_Change_Please",
            username=email[0:30],
            email=email)

    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            user = form.save()

            password_set.send(
                sender=user.__class__,
                request=request,
                user=user,
                password=form.cleaned_data.get('new_password1'),
            )

            messages.success(request, _(
                'Successfully set the new password. Please login now.'))

            return redirect('/')

    else:
        messages.success(request, _('Please set a password.'))
        form = SetPasswordForm(user)

    return render(request, 'registration/password_set_form.html', {
        'form': form,
    })
