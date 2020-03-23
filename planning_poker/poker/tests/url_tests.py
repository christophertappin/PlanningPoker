import pytest
import uuid

from django.urls import reverse



def test_view(client):
    url = reverse('index')
    response = client.get(url)
    assert response.status_code == 200

def test_createsession_redirects(client):
    url = reverse('create')
    response = client.get(url)
    assert response.status_code == 302
    assert response.url is not None

def test_createsession_creates(client):
    url = reverse('create')
    response = client.get(url, follow=True)
    assert response.status_code == 200