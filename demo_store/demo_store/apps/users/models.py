from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    mobile = models.CharField(max_length=11,unique=True,verbose_name='手机号码')
    # unique 如果为True, 这个字段在表中必须有唯一值，默认值是False
    class Meta:
        db_table='tb_users'
        verbose_name='用户'
        verbose_name_plural=verbose_name