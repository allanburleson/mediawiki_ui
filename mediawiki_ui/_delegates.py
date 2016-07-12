import console
import ui

class WebViewDelegate (object):
    def webview_should_start_load(webview, url, nav_type):
        return True
        
    def webview_did_start_load(webview):
        console.show_activity('Loading...')
        
    def webview_did_finish_load(webview):
        global currenturl
        currenturl = webview.eval_js('window.location.href')
        webview.name = webview.eval_js('document.title').split(' -')[0]
        console.hide_activity()
        
    def webview_did_fail_load(webview, error_code, error_msg):
        console.alert('Error %s' % error_code, error_msg, 'OK', hide_cancel_button=True)
        
        
class tvDelegate(object):
    def __init__(self, items, wv, url, results):   
        self.items = items
        self.currentNumLines = len(items)
        self.currentTitle = None
        self.currentRow = None
        self.wv = wv
        self.wikiurl = url
        self.results = results
        
    def tableview_did_select(self, tableview, section, row):
        self.currentTitle = self.items[row]['title']
        self.currentRow = row
        tableview.reload_data()
        tableview.close()
        self.wv.load_url(self.wikiurl + ('%20'.join(self.results[row].split(' '))))
        
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
