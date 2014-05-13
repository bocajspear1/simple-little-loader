A Python script to make repetitive downloading of frameworks, scripts, files and libraries easier.

Essentially, this allows you to make a personal library of your most used files and easily install them later

Note: This does no dependency management. It just downloads something and places it in the current directory. 

#Usage 

```sll.py view```

Shows all items from the source file

<hr>

```sll.py install <language> <library or framework name> [<version>]```

Installs the given library, script, file or framework to the current directory

* language - the language/category of the installed file
* library or framework name - the name of the file or framework to install
* version(optional) - Indicates the particular version of this file you want to install. If none is given. It defaults to 'latest'

<hr>

```sll.py add <language> <library or framework name> <version> <url> [latest]```

Adds an item to the source file

* language - the language/category of the added file, if the language or category does not exist, it is created
* library or framework name - the name of the file or framework that will be used
* version - Indicates the particular version of this item. You can put a number or 'latest' for this option
* url - The link to the file
* latest(optional) if 'latest' is set, this version will be linked to the latest version

<hr>

```sll.py remove <language> [<library or framework name> [<version>]]]```

Removes a language, library or selected version of a library.

* language - the language/category to remove. If nothing else is set, will remove the entire language or category
* library or framework name - the name of the file or framework that will be removed, if nothing else past this is set, all versions of the item are removed
* version - Indicates the particular version of this item you want to remove. You can put a number or 'latest' for this option