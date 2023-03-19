from django import forms
from django.shortcuts import render
from markdown2 import Markdown
from . import util
from django.urls import reverse
from django.http import HttpResponseRedirect
from random import choice
import re

class NewEntryForm(forms.Form):
    title = forms.CharField(label="New Entry Title")
    entry = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Enter Markdown text here...'}), label="")

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
    })

def entry(request, entry):
    markdowner = Markdown()
    if util.get_entry(entry) != None:
        return render(request, "encyclopedia/entry.html", {
            "entry": markdowner.convert(util.get_entry(entry)),
            "title": entry
        })
    elif entry == 'random':
        entry = choice(util.list_entries())
        return HttpResponseRedirect(reverse('entry', kwargs={'entry': entry}))
    else:
        return render(request, "encyclopedia/oops.html")
    
def new(request):
    entries = util.list_entries()
    if request.method == "POST":    
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            entry = form.cleaned_data["entry"]
            if title not in entries:
                with open(f"entries/{title}.md", "w") as file:
                    file.write(entry)
                return HttpResponseRedirect(reverse('entry', kwargs={'entry': title}))
            else:
                return render(request, "encyclopedia/exists.html")
    return render(request, "encyclopedia/new.html", {
        "form": NewEntryForm()
    })

def edit(request, entry):
    form = NewEntryForm()
    form.fields['title'].initial = entry
    form.fields['entry'].initial = util.get_entry(entry)
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            input = form.cleaned_data["entry"]
            with open(f'entries/{title}.md', "w") as file:
                file.write(input)
            return HttpResponseRedirect(reverse('entry', kwargs={'entry': entry}))
    return render(request, "encyclopedia/edit.html", {
        "entry": util.get_entry(entry),
        "form": form
    })

def search(request):
    entries = util.list_entries()
    input = request.POST
    if input["q"] in entries:
        return HttpResponseRedirect(reverse('entry', kwargs={'entry': input["q"]}))  # if found, redirects to page
    else:
        results = []
        for entry in entries:
            print(entry)
            if re.search(f'{input["q"].lower()}', entry.lower()) != None:
                results.append(entry)
        return render(request, "encyclopedia/results.html", {
            "search": input["q"],
            "results": results,
        })