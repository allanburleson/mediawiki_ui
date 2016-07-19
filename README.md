# mediawiki_ui

**mediawiki_ui** is a [Pythonista](http://omz-software.com/pythonista/index.html) module for a nicer iOS user interface for MediaWiki wikis. You can use it with Wikipedia, Gamepedia, Wikia, and any other wikis using MediaWiki.

Put the `mediwiki_ui` folder in `site-packages` and `mwapp.py` wherever you want.

## Use
The easiest way to use this is to run mwapp.py.  

If you want to make your own app with the classes then continue reading.  
Creating an instance of the `wiki.Wiki` class will open the main interface.  
You must have arguments for the title, wiki URL, and extension where the wiki is located.  
Example: `w = wiki.Wiki('Wikipedia', 'https://en.wikipedia.org/', '/wiki')`  
The "extension" is needed because it can very between wikis. It is normally `/wiki`, but not always. It might be `index.php` or `/w`.

## Acknowlegements
Many thanks go to members Pythonista community for their assistance.

## TODO

- [x] Make the loading of articles look nicer
	- [x] Make custom CSS styles
	- [x] Make urls work with reader thing
- [x] Add open in Safari button
- [ ] Add font changer
- [x] Implement history
- [x] Make external URLs work
- [ ] Improve PEP-8 compliance
- [x] Add Wikia support
- [x] Document with comments
- [x] Create an interface for switching between wikis
