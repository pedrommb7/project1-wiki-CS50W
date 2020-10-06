import random
import markdown2

from django import forms
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.files.storage import default_storage

from . import util



# Create your views/pages here.


# Form used in sidebar to search through entry titles
class SearchForm(forms.Form):
    query = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder': 'Search Wiki', 'style': 'width:100%'}))

# Form used to create a new entry/page
class NewPageForm(forms.Form):
    title = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder': 'Enter title', 'id': 'new-entry-title'}))
    data = forms.CharField(label="", widget=forms.Textarea(attrs={'id': 'new-entry'}))

# Form used to edit a entry/page
class EditPageForm(forms.Form):
    title = forms.CharField(label="", widget=forms.TextInput(attrs={
        'id': 'edit-entry-title'}))
    data = forms.CharField(label="", widget=forms.Textarea(attrs={
        'id': 'edit-entry'}))

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def edit(request):
    return render(request, "encyclopedia/edit.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    entry = util.get_entry(title)
    # If url specified is not in entry/page list, return error page
    if entry is None:
        return render(request, "encyclopedia/error.html", {
            "title": title,
            "form": SearchForm()
        })
    # Take user to the entry for the title. Url: (wiki/title)
    else:
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "entry": markdown2.markdown(entry),
            "entry_raw": entry,
            "form": SearchForm()
        })


def newPage(request):
    if request.method == "POST":
        new_entry = NewPageForm(request.POST) #Gets info from form
        # Check if input fields are valid
        if new_entry.is_valid():
            # Extract title of new entry
            title = new_entry.cleaned_data["title"]
            data = new_entry.cleaned_data["data"]
            # Check if entry exists with title
            entries_all = util.list_entries()
            # If entry exists, return same page with error
            for entry in entries_all:
                if entry.lower() == title.lower():
                    return render(request, "encyclopedia/newPage.html", {
                        "form": SearchForm(),
                        "newPageForm": NewPageForm(),
                        "error": "That entry already exists!"
                    })
            # Added markdown for content of entry
            new_entry_title = "# " + title
            # A new line is appended to seperate title from content
            new_entry_data = "\n" + data
            # Combine the title and data to store as content
            new_entry_content = new_entry_title + new_entry_data
            # Save the new entry with the title
            util.save_entry(title, new_entry_content)
            entry = util.get_entry(title)
            # Return the page for the newly created entry
            return render(request, "encyclopedia/entry.html", {
                "title": title,
                "entry": markdown2.markdown(entry),
                "form": SearchForm()
            })
    # Default values
    return render(request, "encyclopedia/newPage.html", {
        "form": SearchForm(),
        "newPageForm": NewPageForm()
    })

# Search for wiki entry
def search(request):
    value = request.GET.get('q','')
    if(util.get_entry(value) is not None):
        return HttpResponseRedirect(reverse("entry", kwargs={'title': value }))
    else:
        subStringEntries = []
        for entry in util.list_entries():
            if value.upper() in entry.upper():
                subStringEntries.append(entry)

        return render(request, "encyclopedia/index.html", {
        "entries": subStringEntries,
        "search": True,
        "value": value
    })

# Edit wiki entry
def editEntry(request, title):
    if request.method == "POST":
        # Get data for the entry to be edited
        entry = util.get_entry(title)
        # Display content in textarea
        edit_form = EditPageForm(initial={'title': title, 'data': entry})
        # Return the page with forms filled with entry information
        return render(request, "encyclopedia/edit.html", {
            "form": SearchForm(),
            "editPageForm": edit_form,
            "entry": entry,
            "title": title
        })

# Submit wiki edit
def submitEditEntry(request, title):
    if request.method == "POST":
        # Extract information from form
        edit_entry = EditPageForm(request.POST)
        if edit_entry.is_valid():
            # Extract 'data' from form
            content = edit_entry.cleaned_data["data"]
            # Extract 'title' from form
            title_edit = edit_entry.cleaned_data["title"]
            # If the title is edited, delete old file
            if title_edit != title:
                filename = f"entries/{title}.md"
                if default_storage.exists(filename):
                    default_storage.delete(filename)
            # Save new entry
            util.save_entry(title_edit, content)
            # Get the new entry 
            entry = util.get_entry(title_edit)
            msg_success = "Successfully updated!"
        # Return the edited entry
        return render(request, "encyclopedia/entry.html", {
            "title": title_edit,
            "entry": markdown2.markdown(entry),
            "form": SearchForm(),
            "msg_success": msg_success
        })

def randomEntry(request):
    # Get list of all entries
    entries = util.list_entries()
    # Get the title of a randomly selected entry
    title = random.choice(entries)
    # Get the content of the selected entry
    entry = util.get_entry(title)
    # Return the redirect page for the entry
    return HttpResponseRedirect(reverse("entry", args=[title]))