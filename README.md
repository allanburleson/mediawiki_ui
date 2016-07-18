# mediawiki_ui

**mediawiki_ui** is a [Pythonista](http://omz-software.com/pythonista/index.html) module for a nicer iOS user interface for MediaWiki wikis. You can use it with Wikipedia, Gamepedia, Wikia, and any other wikis using MediaWiki.

Put the `mediwiki_ui` folder in `site-packages` and `mwapp.py` wherever you want.

## Use
The easiest way to use this is to run mwapp.py.  

If you want to make your own app with the classes then continue reading.  
Creating an instance of the `wiki.Wiki` class will open the main interface.  
You must have an argument for the wiki URL.  
Example: `w = wiki.Wiki('https://wikipedia.org/wiki/')`  
This URL MUST be the full URL for the wiki (`https://wikipedia.org/wiki`, not `https://wikipedia.org`). Since the end of wiki URLs can vary, the script won't crash but not using the full URL can cause weird bugs.

## Acknowlegements
Many thanks go to members Pythonista community for their assistance.

## TODO

- [x] Make the loading of articles look nicer
	- [x] Make custom CSS styles
	- [x] Make urls work with reader thing
- [x] Add open in Safari button
- [ ] Add font changer
- [x] Implement history
- [ ] Make external URLs work
- [x] Add Wikia support
- [x] Document with comments
- [x] Create an interface for switching between wikis
