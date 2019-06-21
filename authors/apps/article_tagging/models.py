from django.db import models
from django.contrib.postgres.fields import ArrayField
# Create your models here.

class ArticleTagging(models.Model):
    #this holds the model for a single tag

    tag_name = models.CharField(unique=True, max_length=50)

    
