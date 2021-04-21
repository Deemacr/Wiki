import random

from django import forms
from django.shortcuts import render

from . import util
from django.shortcuts import redirect
from markdown2 import Markdown

markdowner = Markdown()

class SearchForm(forms.Form):
    search_query = forms.CharField(widget=forms.TextInput(attrs={'class' : 'myfieldclass', 'placeholder': 'Search'}))

class CreateForm(forms.Form):
    title = forms.CharField(label= "Title")
    content = forms.CharField(widget=forms.Textarea(), label='')

class EditForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(), label='')

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        'title' : '',
        "form": SearchForm()
    })

def title(request, title):
    entry = util.get_entry(title)
    if entry:
        return render (request, "encyclopedia/title.html",{
            'title' : title,
            'content' : markdowner.convert(entry),
            "form": SearchForm()
        })
    return render(request, "encyclopedia/error.html", {
        "message": 'No such page Found',
        "homepage": '<p><a href=/>Go back to Homepage</p>',
        "form": SearchForm()
    })
    
def search(request):
    entries = util.list_entries()
    searched_results = []
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            search_query = form.cleaned_data["search_query"].lower()
            processed_entries = []
            for i in entries:
                processed_entries.append(i.lower())
                if search_query in processed_entries:
                    return title(request, search_query)
                if search_query in i.lower():
                    searched_results.append(i)
            else: 
                if len(searched_results)== 0:
                    return render(request, "encyclopedia/error.html", {
                        "message": 'There is no results',
                        "homepage": '<p><a href=/>Go back to Homepage</p>',
                        "form": SearchForm()
                    })
            return render(request, "encyclopedia/search_results.html", {
                'searched_results': searched_results, 
                'form': SearchForm()
            })

def create_page(request):
    if request.method == "POST":
            form = CreateForm(request.POST)
            if form.is_valid():
                entries = util.list_entries()
                entry_name = form.cleaned_data['title']
                content = form.cleaned_data['content']
                processed_entries = []
                for i in entries:
                    processed_entries.append(i.lower())
                    if entry_name in processed_entries:
                        return render (request, "encyclopedia/error.html", {
                        'form': SearchForm(),
                        'message': 'Such entry is already exist',
                        'homepage': '<p><a href=/>Go back to Homepage</p>'
                        })
                else: 
                    util.save_entry(entry_name, content)
                    return title(request, entry_name)
    else:
        return render(request, "encyclopedia/create.html", {'form': SearchForm(), "create": CreateForm()})


def edit_page(request, title):
    if request.method == "GET":
        entry = util.get_entry(title)
        return render(request, "encyclopedia/edit.html", {
            'form': SearchForm(), 
            "edit": EditForm(initial={'content': entry}),
            'title': title
        })
    else:
        form = EditForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']
            util.save_entry(title, content)
            entry = util.get_entry(title)
            return redirect('title', title=title)

def random_page(request):
        if request.method == 'GET':
            entries = util.list_entries()
            num = random.randint(0, len(entries) - 1)
            entry_random = entries[num]
            entry = util.get_entry(entry_random)
        return redirect('title', title=entry_random)