from django.utils import timezone

from django.db import models


class Profile(models.Model):
    uid = models.BigIntegerField(
        blank=False,
        null=False,
        help_text="Telegram user ID.",
        verbose_name="User ID",
        db_index=True,
    )
    gid = models.BigIntegerField(
        blank=False,
        null=False,
        help_text="Telegram group ID this user has sent message into.",
        verbose_name="Group ID",
        db_index=True,
    )
    has_messages = models.BooleanField(blank=False, null=False, default=False)
    created_at = models.DateTimeField(
        blank=False,
        auto_now_add=True,
        help_text="Date and time the profile was created at.",
        verbose_name="Created at",
    )
    updated_at = models.DateTimeField(
        blank=False,
        auto_now=True,
        help_text="Date and time the profile was updated at.",
        verbose_name="Updated at",
    )
    grace_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Date and time the profile grace period started at.",
        verbose_name="Grace started at",
    )
    warnings = models.IntegerField(
        blank=False,
        null=False,
        help_text="Warnings this user have.",
        verbose_name="Warnings",
        default=0,
    )

    class Meta:
        db_table = "profiles"
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
        unique_together = ("uid", "gid")

    def __repr__(self):
        return f"Profile({self.uid} from {self.gid})"

    def __str__(self):
        return f"{self.uid} from {self.gid}"

    def reset_grace(self):
        self.grace_at = timezone.now()
        self.save()
