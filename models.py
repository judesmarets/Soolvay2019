'''
Created on Apr 11, 2019

@author: groupe62
'''

from django.db import models
from django.db.models.fields import CharField

class User(models.Model):
    username = models.CharField(max_length=30, blank=True, null=True)
    password = models.CharField(max_length=30, blank=True, null=True)
    
    def __str__(self):
        return "%s" % (self.username)
    

    
class Publi(models.Model):
    titre = models.CharField(max_length=30, blank=True, null=True)
    confession = models.TextField()
    TYPE_CHOICES = (('A','Accepté'),('W', 'Waiting'),('R','Rejeté'))
    type= models.CharField(max_length=1, choices=TYPE_CHOICES, default='W')
    

    def __str__(self):
        return "%s" % (self.titre)
    
    
class Hashtag(models.Model):
    text = models.CharField(max_length=100, blank=True, null=True)
    publication = models.ManyToManyField(Publi, related_name='publis_hashtag')
    
    def __str__(self):
        return "%s" % (self.text)
    
class Comment(models.Model):
    comment = models.TextField()
    auteur = models.ForeignKey(User, related_name='auteur', blank=True, null=True, on_delete=models.CASCADE)
    publi = models.ForeignKey(Publi, related_name='publi', blank=True, null=True, on_delete=models.CASCADE)
    
    def __str__(self):
        return "%s : %s (%s)"% (self.publi.titre, self.comment, self.auteur) 
    
class Like(models.Model):
    user_like = models.ForeignKey(User, related_name='user_like', blank=True, null=True, on_delete=models.CASCADE)
    publi_like = models.ForeignKey(Publi, related_name='publi_like', blank=True, null=True, on_delete=models.CASCADE)
    
    def __str__(self):
        return "%s par %s" % (self.publi_like.titre, self.user_like.username)
    
    
class Dislike(models.Model):
    user_dislike = models.ForeignKey(User, related_name='user_dislike', blank=True, null=True, on_delete=models.CASCADE)
    publi_dislike = models.ForeignKey(Publi, related_name='publi_dislike', blank=True, null=True, on_delete=models.CASCADE)
    
    def __str__(self):
        return "%s par %s" % (self.publi_dislike.titre, self.user_dislike.username)    
    
    

class LikeC(models.Model):
    user_like = models.ForeignKey(User, related_name='user_likec', blank=True, null=True, on_delete=models.CASCADE)
    com_like = models.ForeignKey(Comment, related_name='com_like', blank=True, null=True, on_delete=models.CASCADE)
    
    def __str__(self):
        return "%s par %s" % (self.com_like.comment, self.user_like.username)
    
    
class DislikeC(models.Model):
    user_dislike = models.ForeignKey(User, related_name='user_dislikec', blank=True, null=True, on_delete=models.CASCADE)
    com_dislike = models.ForeignKey(Comment, related_name='com_dislike', blank=True, null=True, on_delete=models.CASCADE)
    
    def __str__(self):
        return "%s par %s" % (self.com_dislike.comment, self.user_dislike.username) 


