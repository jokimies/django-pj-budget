import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

class ActiveManager(models.Manager):
    def get_queryset(self):
        return super(ActiveManager, self).get_queryset().filter(is_deleted=False)

class StandardMetadata(models.Model):
    """
    A basic (abstract) model for metadata.
    """
    created = models.DateTimeField(_('Created'), default=datetime.datetime.now)
    updated = models.DateTimeField(_('Updated'), default=datetime.datetime.now)
    is_deleted = models.BooleanField(_('Is deleted'), default=False, db_index=True)
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        self.updated = datetime.datetime.now()
        super(StandardMetadata, self).save(*args, **kwargs)
    
    def delete(self):
        self.is_deleted = True
        self.save()

