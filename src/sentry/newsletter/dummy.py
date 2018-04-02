from __future__ import absolute_import

import six

from collections import defaultdict
from django.utils import timezone

from .base import Newsletter


class NewsletterSubscription(object):
    def __init__(self, user, list_id, list_name=None, list_description=None, email=None, verified=None, subscribed=False, subscribed_date=None, unsubscribed_date=None, **kwargs):
        self.email = user.email or email
        self.list_id = list_id
        self.list_description = list_description
        self.list_name = list_name
        # is the email address verified?
        self.verified = user.email_set.get_or_create(email=user.email)[0].is_verified if verified is None else verified
        # are they subscribed to ``list_id``
        self.subscribed = subscribed
        if subscribed:
            self.subscribed_date = subscribed_date or timezone.now()
        elif subscribed is False:
            self.unsubscribed_date = unsubscribed_date or timezone.now()

    def __getitem__(self, key):
        return getattr(self, key)

    def update(self, verified=None, subscribed=None, subscribed_date=None, unsubscribed_date=None, **kwargs):
        if verified is not None:
            self.verified = verified
        if subscribed is not None:
            self.subscribed = subscribed
        if subscribed_date is not None:
            self.subscribed_date = subscribed_date
        elif subscribed:
            self.subscribed_date = timezone.now()
        if unsubscribed_date is not None:
            self.unsubscribed_date = unsubscribed_date
        elif subscribed is False:
            self.unsubscribed_date = timezone.now()


class DummyNewsletter(Newsletter):
    """
    The ``DummyNewsletter`` implementation is primarily used for test cases. It uses a in-memory
    store for tracking subscriptions, which means its not suitable for any real production use-case.
    """

    def __init__(self):
        self._subscriptions = defaultdict(dict)
        self._optout = set()
        self._enabled = True

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False

    def clear(self):
        self._subscriptions = defaultdict(dict)
        self._optout = set()

    def is_enabled(self):
        return self._enabled

    def get_subscriptions(self, user):
        return {
            'subscriptions': list(six.itervalues(self._subscriptions.get(user) or {}))
        }

    def update_subscription(self, user, list_id=None, create=False, **kwargs):
        if list_id:
            if create:
                self._subscriptions[user].setdefault(list_id, NewsletterSubscription(user, list_id, subscribed=True))
            self._subscriptions[user][list_id].update(**kwargs)
        return self._subscriptions[user]

    def optout_email(self, email, **kwargs):
        self._optout.add(email)
