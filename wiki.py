import console

from bs4 import BeautifulSoup
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
        self.searchurl = wikiurl + '?search='
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
        resdivs = soup.findAll('div', attrs={'class': 'mw-search-result-heading'})
        self.results = []
        if resdivs is not None:
            for div in resdivs:
                self.results.append(div.get_text())
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
        page = console.input_alert('Search', '', self.previousSearch, 'Search')
        self.search(page)
             
    def home(self, sender=None):
        self.loadPage(self.wikiurl)
