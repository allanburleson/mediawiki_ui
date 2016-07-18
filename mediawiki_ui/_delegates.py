import console
import ui

class WebViewDelegate (object):
    def __init__(self, wki):
        global wiki, url
        url = ''
        wiki = wki
        
    def webview_should_start_load(webview, pgurl, nav_type):
        global url
        if not pgurl.startswith(wiki.basewikiurl) and pgurl != 'about:blank':
            url = pgurl
            return True
        # The pages loaded with load_html are about:blank
        elif pgurl == 'about:blank':
            url = wiki.currentpage
            return True
        else:
            wiki.loadPage(pgurl)
            return False
        
    def webview_did_start_load(webview):
        # Tell the user that the page is loading
        console.show_activity('Loading...')
        
    def webview_did_finish_load(webview):
        # Get page title with some JavaScript
        currenturl = webview.eval_js('window.location.href')
        webview.name = webview.eval_js('document.title').split(' -')[0]
        console.hide_activity()
        if url and not wiki.back:
            wiki.history.append(url)
            wiki.histIndex += 1
        
    def webview_did_fail_load(webview, error_code, error_msg):
        print('Error %s' % error_code, error_msg)
        
        
class SearchTableViewDelegate(object):
    def __init__(self, items, wv, wiki, url, results):   
        self.items = items
        self.currentNumLines = len(items)
        self.currentTitle = None
        self.currentRow = None
        self.wv = wv
        self.wikiurl = url
        self.wiki = wiki
        self.results = results
        
    def tableview_did_select(self, tableview, section, row):
        # Load page from selected search result
        self.currentTitle = self.items[row]['title']
        self.currentRow = row
        tableview.reload_data()
        tableview.close()
        self.wiki.loadPage(self.wikiurl + 
                         ('%20'.join(self.results[row].split(' '))))
        
    def tableview_did_deselect(self, tableview, section, row):
        pass

    def tableview_title_for_delete_button(self, tableview, section, row):
        return 'Delete'
        
    def tableview_number_of_sections(self, tableview):
        return 1

    def tableview_number_of_rows(self, tableview, section):
        return self.currentNumLines

    def tableview_cell_for_row(self, tableview, section, row):
        cell = ui.TableViewCell()
        cell.text_label.text =  self.items[row]['title']
        cell.accessory_type = self.items[row]['accessory_type']
        return cell


    def tableview_can_delete(self, tableview, section, row):
        return False

    def tableview_can_move(self, tableview, section, row):
        return False

    def tableview_delete(self, tableview, section, row):
        self.currentNumLines -= 1
        tableview.delete_rows((row,))
        del self.items[row]

    def tableview_move_row(self, tableview, from_section, from_row, to_section, to_row):
        self.items = listShuffle(self.items,from_row,to_row) 
