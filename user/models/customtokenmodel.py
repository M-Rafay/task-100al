import binascii
import os

from django.db import models
from django.utils.translation import gettext_lazy  as _
from user.models.usermodel import User


class CustomToken(models.Model):
    """
    The default authorization token model.
    """
    # Device type options
    WEB = 1
    IOS = 2
    ANDROID = 3
    DESKTOP = 4
    DEVICE = (
        (WEB, 'Web'),
        (IOS, 'Ios'),
        (ANDROID, 'Android'),
        (DESKTOP, 'Desktop'),
    )
    # User portal options
    vendor = 1
    # ACTUARIAL = 2
    USER_PORTAL = (
        # (AGENT, 'Agent'),
        (vendor, 'vendor'),
    )

    key = models.CharField(_("Key"), max_length=40, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default="")
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    device_type = models.SmallIntegerField(
        choices=DEVICE,
        default=WEB,
    )
    user_portal = models.SmallIntegerField(
        choices=USER_PORTAL,
        default=vendor,
    )

    class Meta:
        verbose_name = _("Token")
        verbose_name_plural = _("Tokens")

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(CustomToken, self).save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key
