# Copyright (C) 2016 Allan Burleson
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from bs4 import BeautifulSoup, Tag
import console
import dialogs
import os
import requests
import shutil
import sys
import threading
import ui
import webbrowser

from ._delegates import WebViewDelegate, SearchTableViewDelegate
        
        
class Wiki(object):
    def __init__(self, wikiname, basewikiurl, wikiurl):
        #os.chdir(self.wikidir)
        self.modulepath = os.path.dirname(os.path.abspath(__file__))
        os.chdir(self.modulepath)
        self.wikidir = os.path.expanduser('~/.mw-' + wikiname)
        if not os.path.isdir(self.wikidir):
            os.mkdir(self.wikidir)
        #shutil.copyfile(self.modulepath + '/normalize.css', self.wikidir + '/normalize.css')
        #shutil.copyfile(self.modulepath + '/skeleton.css', self.wikidir + '/skeleton.css')
        self.webdelegate = WebViewDelegate(self)
        self.SearchTableViewDelegate = SearchTableViewDelegate
        if not wikiurl.endswith('/'):
            wikiurl += '/'
        # Create URLs
        #assert basewikiurl in wikiurl, 'basewikiurl must be in wikiurl'
        assert not wikiurl.startswith('http'), 'must be end of wiki url'
        if basewikiurl.endswith('/'):
            basewikiurl = basewikiurl[:-1]
        self.basewikiurl = basewikiurl
        self.wikiurl = self.basewikiurl + wikiurl
        self.searchurl = self.wikiurl + 'Special:Search?search='
        self.history = []
        self.histIndex = 0
        self.back = False
        self.closed = False
        if len(sys.argv) > 2:
            self.args = True
        else:
            self.args = False
        # Create WebView
        self.webview = ui.WebView()
        self.mainSource = ''
        self.webview.delegate = WebViewDelegate
        self.loadPage(self.wikiurl)
        self.searchButton = ui.ButtonItem(image=ui.Image.named('iob:ios7_search_24'), action=self.searchTapped)
        self.reloadButton = ui.ButtonItem(image=ui.Image.named('iob:refresh_24'), action=self.reloadTapped)
        self.backButton = ui.ButtonItem(image=ui.Image.named('iob:arrow_left_c_24'), action=self.backTapped)
        self.fwdButton = ui.ButtonItem(image=ui.Image.named('iob:arrow_right_c_24'), action=self.fwdTapped)
        self.homeButton = ui.ButtonItem(image=ui.Image.named('iob:home_24'), action=self.home)
        self.shareButton = ui.ButtonItem(image=ui.Image.named('iob:share_24'), action=self.share)
        self.safariButton = ui.ButtonItem(image=ui.Image.named('iob:compass_24'), action=self.safari)
        self.webview.right_button_items = [self.searchButton, self.reloadButton, self.fwdButton, self.backButton, self.homeButton]
        self.webview.left_button_items = [self.shareButton, self.safariButton]
        self.webview.present('fullscreen', animated=True)
        self.previousSearch = ''
        if len(sys.argv) > 1:
            self.search(sys.argv[1])
        closeThread = threading.Thread(target=self.waitForClose)
        closeThread.start()
        
    def waitForClose(self):
        self.webview.wait_modal()
        self.closed = True
            
    def closeAll(self):
        try:
            self.webview.close()
        except:
            pass
        try:
            self.tv.close()
        except:
            pass
                        
    def search(self, sch, ret=False):
        # Remove extra characters
        sch = sch.strip().strip(',').strip('.')
        self.previousSearch = sch
        console.show_activity('Searching...')
        url = self.searchurl + sch
        req = requests.get(url)
        req.raise_for_status()
        console.hide_activity()
        # Show search results in table view unless the search redirects
        # to a wiki page
        if req.url.startswith(self.searchurl):
            return False if ret else self.showResults(url)
        else:
            return req.url if ret else self.loadPage(req.url)
           
    def showResults(self, search):
        soup = BeautifulSoup(requests.get(search).text, 'html5lib')
        # Figure out what class the search results are in
        if 'wikia.com' in self.wikiurl:
            elems = soup.findAll('a', attrs={'class': 'result-link'})
        else:
            elems = soup.findAll('div', attrs={'class': 'mw-search-result-heading'})
        self.results = []
        if elems is not None:
            for elem in elems:
                # Remove URLs from result list
                if 'http' not in elem.get_text():
                    self.results.append(elem.get_text())
        if len(self.results) == 0:
            console.hud_alert('No results', 'error')
            return
        itemlist = [{'title': result, 'accessory_type':'none'} for result in self.results]
        vdel = SearchTableViewDelegate(itemlist, self.webview, self, self.wikiurl, self.results)
        self.tv = ui.TableView()
        self.tv.name = soup.title.text.split(' -')[0]
        self.tv.delegate = self.tv.data_source = vdel
        self.tv.present('fullscreen')
         
    def loadPage(self, url, regen=False):
        fn = self.fileFromUrl(url)
        fpath = self.wikidir + '/' + fn
        if os.path.isfile(fpath) and regen is False:
            filename = fn
            soup = BeautifulSoup(open(fpath, encoding='utf-8').read(), 'html.parser')
            links = []
            for link in soup.find_all('a'):
                #
                if link.get('href'):
                    if self.basewikiurl in link['href']:
                        links.append(link['href'])
            self.genMorePages(links)
        else:
            console.show_activity('Formatting page...')
            filename = self.genPage(url)
            console.hide_activity()
        self.currentpage = url
        self.webview.load_html(open(fpath, encoding='utf-8').read())
        
    def genPage(self, url, more=True):
        pagetxt = requests.get(url).text
        s = BeautifulSoup(pagetxt, 'html.parser')
        if 'wikia.com' in self.wikiurl:
            body = s.find(id='mw-content-text')
        else:
            body = s.find(id='bodyContent')
        articletxt = str(body)
        soup = BeautifulSoup(articletxt, 'html.parser')
        links = soup.find_all('a')
        plinks = []
        for link in links:
            if link.get('href'):
                if not link['href'].startswith('http'):
                    link['href'] = self.basewikiurl + link['href']
                    plinks.append(link['href'])
        if more:  
            self.genMorePages(plinks)
        imgs = soup.find_all('img')
        for img in imgs:
            if img.get('src'):
                img['src'] = self.basewikiurl + img['src']
            if img.get('srcset'):
                del img.attrs['srcset']
        normalize = open('normalize.css', 'r', encoding='utf-8').read()
        skeleton = open('skeleton.css', 'r', encoding='utf-8').read()
        articletxt = soup.prettify()
        articletxt = '''
        <!DOCTYPE html>
        <html>
            <head>
                <style>
                {}
                </style>
                <style>
                {}
                </style>
                <title>{}</title>
            </head>
            <body>
            {}
            </body>
        </html>
        '''.format(normalize, skeleton, s.title.text, articletxt)
        filename = self.fileFromUrl(url)
        file = open(self.wikidir + '/' + filename, 'w', encoding='utf-8')
        file.write(articletxt)
        file.close()
        return filename
        
    @ui.in_background
    def genMorePages(self, urls):
        usedurls = []
        for url in urls:
            fn = self.fileFromUrl(url)
            if not os.path.isfile(fn):
                usedurls.append(url)
        for url in usedurls:
            if self.closed:
                return
            #print('{}% done, parsing {}'.format(int(usedurls.index(url) + 1 / 
            #                                    len(usedurls)), url))
            self.genPage(url, False)
        
    def fileFromUrl(self, url):
        filename = None
        try:
            filename = url.split('//')[1].split('/')[2]
        except IndexError:
            pass
        if not filename:
            filename = 'main.html'
        if not filename.endswith('.html'):
            filename += '.html'
        return filename
                            
    def reloadTapped(self, sender):
        thread = threading.Thread(target=self.loadPage, args=(self.currentpage, True))
        thread.start()
        
    def backTapped(self, sender):
        if len(self.history) > 1:
            self.back = True
            self.getHistoryPage(self.history[self.histIndex - 2])
            self.histIndex -= 1
            self.back = False
    
    def fwdTapped(self, sender):
        if len(self.history) > 1:
            #self.getHistoryPage(self.history)
            self.back = True
            self.getHistoryPage(self.history[self.histIndex - 1])
            self.histIndex -= 1
            self.back = False
        
    def getHistoryPage(self, url):
        if url in self.basewikiurl:
            self.loadPage(url)
        else:
            self.webview.load_url(url)
                      
    def searchTapped(self, sender):
        page = console.input_alert('Enter search terms', '', self.previousSearch, 'Go')
        self.search(page)
             
    def home(self, sender=None):
        self.loadPage(self.wikiurl)
    
    def share(self, sender):
        dialogs.share_url(self.currentpage)
        
    def safari(self, sender):
        webbrowser.open('safari-' + self.currentpage)
        

if __name__ == '__main__':
    w = Wiki('coppermind', 'http://coppermind.net', '/wiki')
