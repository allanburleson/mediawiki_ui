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
        
        
class tvDelegate(object): #also acts as the data_source.  Can be separate, but this is easier.  
    def __init__(self, items, wv, url, results):   
        self.items = items
        self.currentNumLines = len(items)
        self.currentTitle = None
        self.currentRow = None
        self.wv = wv
        self.wikiurl = url
        self.results = results
        
    def tableview_did_select(self, tableview, section, row):
        # Called when a row was selected.
        self.currentTitle = self.items[row]['title']
        self.currentRow = row # needed for the test above
        tableview.reload_data() # forces changes into the displayed list
        tableview.close()
        self.wv.load_url(self.wikiurl + ('%20'.join(self.results[row].split(' '))))
        
    def tableview_did_deselect(self, tableview, section, row):
        # Called when a row was de-selected (in multiple selection mode).
        pass

    def tableview_title_for_delete_button(self, tableview, section, row):
        # Return the title for the 'swipe-to-***' button.
        return 'Delete'
        
    def tableview_number_of_sections(self, tableview):
        # Return the number of sections (defaults to 1). Someone else can mess with 
        # sections and section logic
        return 1

    def tableview_number_of_rows(self, tableview, section):
        # Return the number of rows in the section
        return self.currentNumLines #needed to be in sync with displayed version, 

    def tableview_cell_for_row(self, tableview, section, row):
        # Create and return a cell for the given section/row
        cell = ui.TableViewCell()
        cell.text_label.text =  self.items[row]['title']
        cell.accessory_type = self.items[row]['accessory_type']
        return cell


    def tableview_can_delete(self, tableview, section, row):
        # Return True if the user should be able to delete the given row.
        return False # you can use logic to lock out specific ("pinned" entries) 

    def tableview_can_move(self, tableview, section, row):
        # Return True if a reordering control should be shown for the given row (in editing mode).
        return False # see above

    def tableview_delete(self, tableview, section, row):
        # Called when the user confirms deletion of the given row.
        self.currentNumLines -= 1 # see above regarding hte "syncing"
        tableview.delete_rows((row,)) # this animates the deletion  could also 'tableview.reload_data()'
        del self.items[row]

    def tableview_move_row(self, tableview, from_section, from_row, to_section, to_row):
        # Called when the user moves a row with the reordering control (in editing mode).
        
        self.items = listShuffle(self.items,from_row,to_row) 
        # cynchronizes what is displayed with the underlying list
