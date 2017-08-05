# -*- coding: utf-8 -*-
"""Helper utilities and decorators."""
from flask import flash
import requests


def flash_errors(form, category='warning'):
    """Flash all errors for a form."""
    for field, errors in form.errors.items():
        for error in errors:
            flash('{0} - {1}'.format(getattr(form, field).label.text, error), category)


def send_html_email(sender, subject, to, bcc, html):
    try:
        return requests.post(
            "https://api.mailgun.net/v3/areasonforliving.com/messages",
            auth=("api", "key-f60af287775bbf5807c978339b701aed"),
            data={"from": sender,
                  "to": to,
                  "bcc": bcc,
                  "subject": subject,
                  "html": html,
                  "o:require-tls": False,
                  "o:skip-verification": False})
    except:
        return requests.post(
          "https://api.mailgun.net/v3/myground.org/messages",
          auth=("api", "key-f60af287775bbf5807c978339b701aed"),
          data={"from": sender,
                "to": to,
                "bcc": bcc,
                "subject": subject,
                "html": html}, verify=False)
