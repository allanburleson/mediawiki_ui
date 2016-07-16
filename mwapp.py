import dialogs
import os
import shelve
import sys
from time import sleep
import ui

from mediawiki_ui.wiki import Wiki


class TableViewDelegate(object):
    def __init__(self, wikis):   
        self.wikis = wikis
        self.items = []
        for wiki in self.wikis:
            self.items.append(wiki)
        self.currentNumLines = len(self.items)
        self.currentTitle = None
        self.currentRow = None
        
    def tableview_did_select(self, tableview, section, row):
        self.currentTitle = tableview.data_source.items[row]
        self.currentRow = row
        tableview.reload_data()
        for wiki in self.wikis:
            # Find wiki URL and load it
            if wiki == tableview.data_source.items[row]['title']:
                w = Wiki(self.wikis[wiki])
        
    def tableview_did_deselect(self, tableview, section, row):
        pass

    def tableview_title_for_delete_button(self, tableview, section, row):
        return 'Delete'
        
    def tableview_number_of_sections(self, tableview):
        return 1
        
    def tableview_accessory_button_tapped(self, tableview, section, row):
        fields=[{'type': 'text', 'key': 'title', 'title': 'Title',
                 'value': tableview.data_source.items[row]['title']},
                {'type': 'url', 'key': 'url', 'title': 'URL',
                 'value': self.wikis[tableview.data_source.items[row]['title']]}]
        urlinfo = 'Make sure that your URL starts with "http://" or "https://" and it is the full'\
                  ' wiki URL ("https://en.wikipedia.org/wiki", not "https://en.wikipedia.org").'
        result = dialogs.form_dialog('Edit Data', sections=(('', fields, urlinfo),))
        if result:
            origTitle = tableview.data_source.items[row]['title']
            tableview.data_source.items[row]['title'] = result['title']
            tableview.reload_data()
            self.wikis[tableview.data_source.items[row]['title']] = result['url']
            del self.wikis[origTitle]
        

class WikiList(object):
    def __init__(self, wikis):
        addbtn = ui.ButtonItem(image=ui.Image.named('iob:ios7_plus_empty_32'), action=self.add)
        # self.editbtn so it can be used in WikiList.edit
        self.editbtn = ui.ButtonItem(title='Edit', action=self.edit)
        items = None
        # If save file exists use it
        if os.path.isfile(os.path.expanduser('~/.mwsave.dat')):
            s = shelve.open(os.path.expanduser('~/.mwsave'))
            try:
                wikis = s['wikis']
            except KeyError:
                pass
            s.close()
        self.tv = ui.TableView(name='Wikis')
        self.nv = ui.NavigationView(self.tv)
        self.tv.delegate = TableViewDelegate(wikis)
        items = []
        # Create data source from dictionary of wikis
        for wiki in wikis:
            items.append({'title': wiki, 'accessory_type': 'detail_disclosure_button'})
        self.tv.data_source = ui.ListDataSource(items)
        self.tv.data_source.move_enabled = True
        self.tv.data_source.edit_action = self.removeFromWikis
        self.tv.right_button_items = [addbtn]
        self.tv.left_button_items = [self.editbtn]
        self.nv.present('fullscreen', hide_title_bar=True)
        # Wait until the view closes to save app data
        self.nv.wait_modal()
        self.save()
          
    def add(self, sender):
        '''Add wiki to list of wikis'''
        fields=[{'type':'text','key':'title','title':'Title'},
                {'type':'url','key':'url','title':'URL','value':'http'}]
        urlinfo = 'Make sure that your URL starts with "http://" or "https://" and it is the full'\
                  ' wiki URL ("https://en.wikipedia.org/wiki", not "https://en.wikipedia.org").'
        result = dialogs.form_dialog('Add Wiki', sections=(('', fields, urlinfo),))
        if result:
            self.tv.data_source.items.append(({'title': result['title'], 'accessory_type': 'detail_disclosure_button'}))
            self.tv.delegate.wikis[result['title']] = result['url']
            self.tv.reload()
    
    def edit(self, sender):
        '''Go into wiki edit mode'''
        def done(sender):
            self.tv.editing = False
            # Change button labeled "Done" to "Edit"
            self.tv.left_button_items = [self.editbtn]
        # Change button labeled "Edit" to "Done"
        donebtn = ui.ButtonItem(title='Done', action=done)
        self.tv.left_button_items = [donebtn]
        self.tv.editing = True
        
    def save(self): 
        '''Save app data'''
        try:
            s = shelve.open(os.path.expanduser('~/.mwsave'))
        except FileNotFoundError:
            open(os.path.expanduser('~/.mwsave.dat'), 'a')
        s['items'] = self.tv.data_source.items
        wikis = {}
        for wiki in self.tv.delegate.wikis:
            wikis[wiki] = self.tv.delegate.wikis[wiki]
        s['wikis'] = wikis
        s.close()
        
    def removeFromWikis(self, sender):
        items = []
        for i in sender.items:
            items.append(i['title'])
        for wiki in self.tv.delegate.wikis:
            if wiki not in items:
                del self.tv.delegate.wikis[wiki]
        

wikis = {'Wikipedia':'https://en.wikipedia.org/wiki'}
app = WikiList(wikis)
