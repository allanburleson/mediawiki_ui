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

from bs4 import BeautifulSoup 
import console
import dialogs
import requests
import sys
import ui

from _delegates import WebViewDelegate, SearchTableViewDelegate


class Wiki(object):
    def __init__(self, basewikiurl, wikiurl):
        self.webdelegate = WebViewDelegate
        self.SearchTableViewDelegate = SearchTableViewDelegate
        if not wikiurl.endswith('/'):
            wikiurl += '/'
        # Create URLs
        assert basewikiurl in wikiurl, 'basewikiurl must be in wikiurl'
        if basewikiurl.endswith('/'):
            basewikiurl = basewikiurl[:-1]
        self.basewikiurl = basewikiurl
        self.wikiurl = wikiurl
        self.searchurl = wikiurl + 'Special:Search?search='
        self.history = []
        self.currenthtml = ''
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
        self.reloadButton = ui.ButtonItem(image=ui.Image.named('iob:ios7_refresh_outline_24'), action=self.reloadTapped)
        self.backButton = ui.ButtonItem(image=ui.Image.named('iob:ios7_arrow_back_24'), action=self.backTapped)
        self.fwdButton = ui.ButtonItem(image=ui.Image.named('iob:ios7_arrow_forward_24'), action=self.fwdTapped)
        self.homeButton = ui.ButtonItem(image=ui.Image.named('iob:home_24'), action=self.home)
        self.webview.right_button_items = [self.searchButton, self.reloadButton, self.fwdButton, self.backButton, self.homeButton]
        self.webview.present('fullscreen', animated=False)
        self.previousSearch = ''
        if len(sys.argv) > 1:
            self.search(sys.argv[1])
            
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
         
    @ui.in_background
    def loadPage(self, url):
        pagetxt = requests.get(url).text
        soup = BeautifulSoup(pagetxt, 'html5lib')
        if 'wikia.com' in self.wikiurl:
            body = soup.find(id='mw-content-text')
        else:
            body = soup.find(id='bodyContent')
        articletxt = str(body)
        css = '''
        a {
            text-decoration: none;
        }
        p, a, div {
            font-family: Helvetica, Arial, sans-serif;
        }
        '''
        articletxt = '''
        <html><head><style>{}</style></head><body>
        '''.format(css) + articletxt + '</body></html>'
        soup = BeautifulSoup(articletxt, 'html5lib')
        links = soup.find_all('a')
        for link in links:
            if link.get('href'):
                if not link['href'].startswith('http'):
                    link['href'] = self.basewikiurl + link['href']
        imgs = soup.find_all('img')
        for img in imgs:
            if img.get('src'):
                img['src'] = self.basewikiurl + img['src']
            if img.get('srcset'):
                del img.attrs['srcset']
        articletxt = soup.prettify()
        self.webview.load_html(articletxt)
        self.history.append(articletxt)
        self.currenthtml = articletxt
                            
    def reloadTapped(self, sender):
        self.webview.load_html(self.currenthtml)
        
    def backTapped(self, sender):
        self.webview.go_back()
    
    def fwdTapped(self, sender):
        self.webview.go_forward()
                      
    def searchTapped(self, sender):
        page = console.input_alert('Enter search terms', '', self.previousSearch, 'Go')
        self.search(page)
             
    def home(self, sender=None):
        self.loadPage(self.wikiurl)
        
if __name__ == '__main__':
    w = Wiki('http://coppermind.net', 'http://coppermind.net/wiki')
