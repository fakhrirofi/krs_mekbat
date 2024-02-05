from django.shortcuts import render
from .models import Post

def index(request):
    return render(request, "blog/home.html", {
        "posts" : Post.objects.order_by("-date")
    })

