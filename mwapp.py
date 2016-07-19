import dialogs
import os
import shelve
import shutil
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
                w = Wiki(wiki, self.wikis[wiki]['url'], self.wikis[wiki]['ext'])
        
    def tableview_did_deselect(self, tableview, section, row):
        pass

    def tableview_title_for_delete_button(self, tableview, section, row):
        return 'Delete'
        
    def tableview_number_of_sections(self, tableview):
        return 1
        
    def tableview_accessory_button_tapped(self, tableview, section, row):
        wiki = self.wikis[tableview.data_source.items[row]['title']]
        wikiname = tableview.data_source.items[row]['title']
        s1fields=[{'type':'text','key':'title','title':'Title','value':wikiname},
                {'type':'url','key':'url','title':'URL','value':wiki['url']}]
        urlinfo = 'Make sure that your URL starts with "http://" or "https://" and it is NOT the full'\
                  ' wiki URL like "https://en.wikipedia.org/wiki." Use "https://en.wikipedia.org" instead.'
        s2fields = [{'type': 'url', 'key': 'extension', 'title': 'Wiki extension','value':wiki['ext']}]
        extInfo = 'What is meant by "Wiki extension" is the end of the wiki\'s url (for Wikipedia it\'s "/wiki.")'
        result = dialogs.form_dialog('Edit Data', sections=(('', s1fields, urlinfo),('', s2fields, extInfo)))
        if result:
            origTitle = tableview.data_source.items[row]['title']
            tableview.data_source.items[row]['title'] = result['title']
            tableview.reload_data()
            self.wikis[tableview.data_source.items[row]['title']] = {'url': result['url'], 'ext': result['extension']}
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
        s1fields=[{'type':'text','key':'title','title':'Title'},
                {'type':'url','key':'url','title':'URL','value':'http'}]
        urlinfo = 'Make sure that your URL starts with "http://" or "https://" and it is NOT the full'\
                  ' wiki URL like "https://en.wikipedia.org/wiki." Use "https://en.wikipedia.org" instead.'
        s2fields = [{'type': 'url', 'key': 'extension', 'title': 'Wiki extension'}]
        extInfo = 'What is meant by "Wiki extension" is the end of the wiki\'s url (for Wikipedia it\'s "/wiki.")'
        result = dialogs.form_dialog('Add Wiki', sections=(('', s1fields, urlinfo),('', s2fields, extInfo)))
        if result:
            self.tv.data_source.items.append(({'title': result['title'], 'accessory_type': 'detail_disclosure_button'}))
            self.tv.delegate.wikis[result['title']] = {'url': result['url'], 'ext': result['extension']}
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
        wikisToDelete = []
        for wiki in self.tv.delegate.wikis:
            if wiki not in items:
                wikisToDelete.append(wiki)
        for w in wikisToDelete:
            print(self.tv.delegate.wikis)
            shutil.rmtree(os.path.expanduser('~/.mw-' + w))
            print(os.path.expanduser('~/.mw-' + w))
            del self.tv.delegate.wikis[w]
        

wikis = {'Esolangs':{'url': 'https://esolangs.org', 'ext': '/wiki'}, 
         'Wikipedia':{'url': 'https://en.wikipedia.org', 'ext': '/wiki'}}
app = WikiList(wikis)
