from flask_app import app
from flask import render_template, redirect, request, session, flash
from flask_app.models.entry import Entry
from flask_app.models import tag
import datetime

@app.route('/dashboard')
def display_dashboard():
    print (datetime.datetime.now().strftime('%Y-%m-%d'))
    print (datetime.datetime.now())
    if not 'user_id' in session:
        return redirect('/')
    return render_template('dashboard.html', date = datetime.datetime.now(), recent_entries = Entry.get_most_recent({'user_id' : session['user_id']}))

# TODO add more navigational endpoints
# [DONE] back button on some entries
# [DONE] add forward button functionality
# [DONE] fix overflow issue on recent entries list (add a button to all entries[non working button])
# [DONE] instead of rerouting to a new page fix html so that it will display a blank journal entry
# [DONE] make a new navigation bar for journal pages NOTE: make it look pretty pls!
# [DONE] work on tags mayhaps uwu owo
# [DONE?] list all posts NOTE: this just needs styling..and a like to the post
# [*] add css animation effects to hoverable assests
# [*] add hover overlay onto recent entries on the home page
# [*] fix navbar on journal entry page so that it looks less awkward idk heheheheh :|
# [*] get the clock on the dashboard to actually work lol :/
# [*] If you EVER have time change the end point for the entry to return json data and use Ajax to render it onto the page 
@app.route('/entry/<string:date>')
def show_entry(date):
    if 'user_id' not in session:
        return redirect('/')

    entry = Entry.get_by_date({'user_id' : session['user_id'], 'entry_date' : date})

    return render_template('entry.html', 
                            entry = entry, 
                            date = datetime.datetime.strptime(date, '%Y-%m-%d'), 
                            offset = datetime.timedelta(days=1),
                            today = datetime.datetime.now().date()
                          )
@app.route('/entry/all')
def show_all():
    if 'user_id' not in session:
        return redirect('/')
    return render_template('entry_all.html', entries = Entry.get_all_user_posts({'user_id' : session['user_id']}))

# ROUTES TO TODAY'S ENTRY
@app.route('/entry/today')
def daily_entry():
    if 'user_id' not in session:
        return redirect('/')

    date_str = datetime.datetime.now().strftime('%Y-%m-%d')

    entry = Entry.get_by_date({'user_id' : session['user_id'], 'entry_date' : date_str})
    if not entry:
        return redirect(f'/entry/new/{date_str}')

    return redirect(f'/entry/{date_str}')

# MAKE A NEW ENTRY
@app.route('/entry/new/<string:date>')
def entry_formed(date):
    if 'user_id' not in session:
        return redirect('/')

    # check to see if entry is already in the database
    # we only want one entry for everyday
    entry = Entry.get_by_date({'user_id' : session['user_id'], 'entry_date' : date})
    if entry:
        return redirect(f'/entry/{date}')

    return render_template('entry_new.html', date = datetime.datetime.strptime(date, '%Y-%m-%d'))

@app.route('/entry/create', methods=['POST'])
def create_entry():
    print(request.form)
    entry_id = Entry.create(request.form)
    # enter new tags
    tags = request.form['tags'].split(',')
    for title in tags:
        if title != '':
            Entry.create_new_entry({'entry_id' : entry_id, 'title' : title})
    return redirect(f'/entry/{request.form["entry_date"]}')

# EDIT ENTRY
@app.route('/entry/edit/<string:date>')
def entry_edit_form(date):
    if 'user_id' not in session:
        return redirect('/')

    entry = Entry.get_by_date({'user_id' : session['user_id'], 'entry_date' : date})
    
    if not entry:
        return redirect(f'/entry/new/{date}')

    if entry.tags[0].id != None:
        tags = ','.join((tag.title for tag in entry.tags))
    else:
        tags = ''

    return render_template('entry_edit.html', entry = entry, tags = tags)

@app.route('/entry/update', methods=['POST'])
def update_entry():
    print(request.form)
    Entry.update_entry(request.form)

    Entry.delete_all_entry_tags({'entry_id' : request.form['id']})
    tags = request.form['tags'].split(',')
    for title in tags:
        if title != '':
            Entry.create_new_entry({'entry_id' : request.form['id'], 'title' : title})

    return redirect(f'/entry/{request.form["entry_date"]}')

# DELETE ENTRY
@app.route('/entry/delete/<int:id>') 
def delete_entry(id):
    Entry.delete_all_entry_tags({'entry_id' : id})
    Entry.delete_entry({'id' : id})
    return redirect('/dashboard')

@app.route('/tag/<int:id>')
def show_tagged_entries(id):
    if 'user_id' not in session:
        return redirect('/logout')
    tagged = tag.Tag.show_all_tagged({'id' : id, 'user_id' : session['user_id']})
    return render_template('tags.html', tag = tagged)