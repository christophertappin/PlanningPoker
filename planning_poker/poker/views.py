from django.shortcuts import render, redirect

import uuid

options = [0, .5, 1, 2, 3, 5, 8, 13]

# Create your views here.
def index(request):
    return render(request, 'poker/index.html', {})

def create_session(request):
    # Create UUID
    uuid_string = str(uuid.uuid4().hex)
    # Redirect
    response = redirect('/' + uuid_string + '/')
    return response

def session(request, id):
    return render(request, 'poker/session.html', {
        'id': id,
        'options': options
    })