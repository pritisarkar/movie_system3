from django.db import models
class User(models.Model):
    email = models.CharField(max_length = 50)
    is_admin = models.BooleanField(default=True)
    password = models.CharField()
    def __str__(self):
        return self.email