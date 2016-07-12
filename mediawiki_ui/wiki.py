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

from ._delegates import WebViewDelegate, tvDelegate


class Wiki(object):
    def __init__(self, wikiurl):
        self.webdelegate = WebViewDelegate
        self.tvdelegate = tvDelegate
        if not wikiurl.endswith('/'):
            wikiurl += '/'
        self.wikiurl = wikiurl
        self.searchurl = wikiurl + 'Special:Search?search='
        if len(sys.argv) > 2:
            self.args = True
        else:
            self.args = False
        self.webview = ui.WebView()
        self.mainSource = ''
        self.loadPage(wikiurl)
        self.webview.delegate = WebViewDelegate
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
        sch = sch.strip().strip(',').strip('.')
        self.previousSearch = sch
        console.show_activity('Searching...')
        url = self.searchurl + sch
        req = requests.get(url)
        req.raise_for_status()
        console.hide_activity()
        if req.url.startswith(self.searchurl):
            return False if ret else self.showResults(url)
        else:
            return req.url if ret else self.loadPage(req.url)
           
    def showResults(self, search):
        soup = BeautifulSoup(requests.get(search).text, 'html5lib')
        if 'wikia.com' in self.wikiurl:
            elems = soup.findAll('a', attrs={'class': 'result-link'})
        else:
            elems = soup.findAll('div', attrs={'class': 'mw-search-result-heading'})
        self.results = []
        if elems is not None:
            for elem in elems:
                if 'http' not in elem.get_text():
                    self.results.append(elem.get_text())
        if len(self.results) == 0:
            console.hud_alert('No results', 'error')
            return
        itemlist = [{'title': result, 'accessory_type':'none'} for result in self.results]
        vdel = tvDelegate(itemlist, self.webview, self.wikiurl, self.results)
        self.tv = ui.TableView()
        self.tv.name = soup.title.text.split(' -')[0]
        self.tv.delegate = self.tv.data_source = vdel
        self.tv.present('fullscreen')
         
    def loadPage(self, url):
        self.webview.load_url(url)
                            
    def reloadTapped(self, sender):
        self.webview.reload()
        
    def backTapped(self, sender):
        self.webview.go_back()
    
    def fwdTapped(self, sender):
        self.webview.go_forward()
                      
    def searchTapped(self, sender):
        page = console.input_alert('Enter search terms', '', self.previousSearch, 'Go')
        self.search(page)
             
    def home(self, sender=None):
        self.loadPage(self.wikiurl)
