from django.db import models

# Create your models here.
class Consumer(models.Model):
    version = models.IntegerField()
    key = models.CharField(max_length=32)
    secret = models.CharField(max_length=32)

    def __unicode__(self):
        return unicode(self.version)

