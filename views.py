'''
Created on Apr 11, 2019

@author: groupe62
'''


from django.shortcuts import render, redirect, reverse
from django.template.context_processors import request
from solvay2019.models import *
from django.http.response import HttpResponse
import re
import hashlib, binascii, os
from django.db.models import Count
from debian.changelog import comments

blacklist = ['pute', 'fuck','poufiasse','connard','enculé','fdp','hitler','ucl','français','barça']
users = User.objects.all()

def hash_password(password):
    """Hash a password for storing."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), 
                                salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')

def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512', 
                                  provided_password.encode('utf-8'), 
                                  salt.encode('ascii'), 
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password



def register(request):
    
    if 'search' in request.GET:
        search = request.GET['search']
        if len(Hashtag.objects.filter(text=search)) >= 1:
            hashtags = Hashtag.objects.get(text=search)
            confessions = hashtags.publication.all()
            return render (request, 'home.html', {'post': confessions})
        else :
            return render (request, 'register.html', {'error3': 'Pas de résultat'})
    
    
    if 'username' in request.GET:
        password = request.GET['password']
        enteredusername = request.GET['username']
        user = User(username=request.GET['username'],
                    password= password)        
        if re.match(r'[A-Za-z0-9@#$%^&+=]{8,}', password):
            if len(User.objects.filter(username=enteredusername)) == 1:
                return render(request, 'register.html', {'error1': 'This username is already used.'})
            elif request.GET['password'] != request.GET['confirmpassword']:
                return render(request, 'register.html', {'error': 'Passwords do not match.'})
            else:
                stored_password = hash_password(password)
                user = User(username = request.GET['username'],
                            password = stored_password)
                user.save()
                request.session['user_id'] = user.id
                return redirect(home)
        else:
            return render (request, 'register.html', {'error2' : 'Password must be at least 8 characters and may only contain letters, numbers and @#$%^&+='})
    else :
        return render(request, 'register.html')


    
def home(request):
    user = None
    confessions = Publi.objects.all()

    
    if 'search' in request.GET:
        search = request.GET['search']
        if len(Hashtag.objects.filter(text=search)) >= 1:
            hashtags = Hashtag.objects.get(text=search)
            confessions = hashtags.publication.all()
        
        
    if 'user_id' in request.session:
        user = User.objects.get(id=request.session['user_id'])
        if 'commentaire' in request.GET:
            publi = Publi.objects.get(id=request.GET['postCom'])
            text = request.GET['commentaire']
            text = re.sub(r'\b\w*\b', replace, text, flags=re.I|re.U)
            commentaire = Comment(comment = text,
                                  auteur = user,
                                  publi = publi)
            commentaire.save()
        if 'postLike' in request.GET:
            publi_like = Publi.objects.get(id=request.GET['postLike'])
            if len(Like.objects.filter(user_like = user, publi_like = publi_like)) == 0:
                new_like = Like(user_like = user,
                            publi_like = publi_like)
                new_like.save()
                
        if 'postDislike' in request.GET:
            publi_dislike = Publi.objects.get(id=request.GET['postDislike'])
            if len(Dislike.objects.filter(user_dislike = user, publi_dislike = publi_dislike)) == 0:    
                new_dislike = Dislike(user_dislike = user,
                            publi_dislike = publi_dislike)
                new_dislike.save()
                
        if 'comLike' in request.GET:
            com_like = Comment.objects.get(id=request.GET['comLike'])
            if len(LikeC.objects.filter(user_like = user, com_like = com_like)) == 0:
                new_likec = LikeC(user_like = user,
                            com_like = com_like)
                new_likec.save()
                
        if 'comDislike' in request.GET:
            com_dislike = Comment.objects.get(id=request.GET['comDislike'])
            if len(DislikeC.objects.filter(user_dislike = user, com_dislike = com_dislike)) == 0:
                new_dislikec = DislikeC(user_dislike = user,
                            com_dislike = com_dislike)
                new_dislikec.save()
        
    return render (request, 'home.html', {'post': confessions, 'user': user})


def login(request):
    
    if 'search' in request.GET:
        search = request.GET['search']
        if len(Hashtag.objects.filter(text=search)) >= 1:
            hashtags = Hashtag.objects.get(text=search)
            confessions = hashtags.publication.all()
            return render (request, 'home.html', {'post': confessions})
        else :
            return render (request, 'login.html', {'error1': 'Pas de résultat'})
    
       
    if 'username' in request.GET and 'password' in request.GET:
        username= request.GET['username']
        if len(User.objects.filter(username=username)) == 1:
            user_ut = User.objects.get(username = username)
            comments = user_ut.auteur.all()
            print(comments)
            for i in comments:
                nb_dislikes = i.com_dislike.all()
                if len(nb_dislikes) >= 3:
                    return render(request, 'DjangoUnchained.html', {'error': "Dégage t'es banni !!!"})
            password = request.GET['password']
            username = request.GET['username']
            user_1 = User.objects.get(username = username)
            stored_password = user_1.password
            
            if verify_password(stored_password, password) == True :
                user = User.objects.get(username=username)
                request.session['user_id'] = user.id
                return redirect(home)
            
    
            else:
                return render(request, 'login.html', {'error': 'Incorrect password'})
        else:
            return render(request, 'login.html', {'error': 'Username does not exist'})
    else: 
        return render(request, 'login.html')
    
    
def replace(match):
    word = match.group()
    if word.lower() in blacklist:
        return '*' * len(word)
    else:
        return word 
    
def replaceh(match):
    word = match.group()
    if word.lower() in blacklist:
        return 'beeeep'
    else:
        return word     
    
def publication(request):
    
    if 'search' in request.GET:
        search = request.GET['search']
        if len(Hashtag.objects.filter(text=search)) >= 1:
            hashtags = Hashtag.objects.get(text=search)
            confessions = hashtags.publication.all()
            return render (request, 'home.html', {'post': confessions})
        else :
            return render (request, 'publication.html', {'error': 'Pas de résultat'})
    
    
    if 'confession' in request.GET and 'titre' in request.GET and 'hashtags' in request.GET:
        titre = request.GET['titre']
        titre = re.sub(r'\b\w*\b', replace, titre, flags=re.I|re.U)
        text = request.GET['confession']
        text = re.sub(r'\b\w*\b', replace, text, flags=re.I|re.U)
        confession = Publi(titre=titre,
                      confession=text)
        confession.save()
        hashtags= request.GET['hashtags']
        text = re.sub(r'\b\w*\b', replaceh, hashtags, flags=re.I|re.U)
        listhashtags = text.split()
        print(listhashtags)
        for v in listhashtags:
            if len(Hashtag.objects.filter(text=v)) == 1:
                hashtags = Hashtag.objects.get(text=v)
                hashtags.save()
                hashtags.publication.add(confession)
                
            else:     
                hashtags = Hashtag(text=v)
                hashtags.save()
                hashtags.publication.add(confession)
                
        return redirect('/home')
    else :
              
        return render(request, 'publication.html')




def logout(request):
    
    if 'user_id' in request.session:
        del request.session['user_id']
        request.session['message'] = 'You were successfully disconnected'
        return redirect(home)
    else:
        return redirect(home)
    
    
    
def top10(request):
    
    
    if 'user_id' in request.session:
        user = User.objects.get(id=request.session['user_id'])
    
    
    dict_hashtags = Hashtag.objects.all().values('text').annotate(total=Count('publication')).order_by('-total')[:5]
    dict_tops = Publi.objects.all().values('confession', 'titre').annotate(total=Count('publi_like')).order_by('-total')[:3]
    dict_flops = Publi.objects.all().values('confession', 'titre').annotate(total=Count('publi_dislike')).order_by('-total')[:3]
    print(dict_flops)
    
    
    if 'search' in request.GET:
        search = request.GET['search']
        if len(Hashtag.objects.filter(text=search)) >= 1:
            hashtags = Hashtag.objects.get(text=search)
            confessions = hashtags.publication.all()
            return render (request, 'home.html', {'post': confessions})
        else :
            return render (request, 'top10.html', {'dict_hashtags': dict_hashtags, 'dict_tops': dict_tops, 'dict_flops': dict_flops, 'error': 'Pas de résultat'})   
    
     
    return render (request, 'top10.html', {'dict_hashtags': dict_hashtags, 'dict_tops': dict_tops, 'dict_flops': dict_flops})    



def validation(request):
    
    confessions = Publi.objects.all()
    if 'confirm' in request.GET:
        publi = Publi.objects.get(id=request.GET['confirm'])
        publi.type = 'A'
        publi.save()
        return render(request, 'validation.html', {'post': confessions})
    
    if 'reject' in request.GET:
        publi = Publi.objects.get(id=request.GET['reject'])
        publi.type = 'R'
        publi.save()
        return render(request, 'validation.html', {'post': confessions})
          
    else :    
        return render (request, 'validation.html', {'post': confessions})

def Vlogin(request):
    
    if 'password' in request.GET:
        entered_password = request.GET['password']
        if entered_password == 'moderator123':
            return redirect(validation)
        else:    
            return render (request, 'Vlogin.html', {'error': 'Incorrect Password'})

    return render(request, 'Vlogin.html')

def DjangoUnchained(request):
    
    return render(request, 'DjangoUnchained.html')

