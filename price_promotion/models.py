from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class File(models.Model):
    userName = models.OneToOneField(User,on_delete=models.CASCADE)
    file = models.FileField(upload_to="videos",null=True,blank=True)

    def __str__(self) -> str:
        return self.userName.username