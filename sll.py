#!/usr/bin/env python3

import sys
import json
import urllib.request
import os
import subprocess
import shutil
import zipfile
import re
import tarfile

VERSION = "0.2"

SCRIPT_LOCATION = os.path.dirname(os.path.realpath(__file__))
SOURCE_FILE_PATH = SCRIPT_LOCATION + "/sll-source.json"
running_command = ""
running_version = ""
running_lib = ""
running_language = ""

if not os.path.isfile(SOURCE_FILE_PATH ):
	error ("Could not find source file (sll-source.json)")
	exit(1)
	
SOURCE_FILE = open(SOURCE_FILE_PATH , "r")
contents = SOURCE_FILE.read()
if contents != "":
	SOURCE_JSON = json.loads(contents)
else:
	SOURCE_JSON = {}
	
SOURCE_FILE.close()

def main():
	
	if (len(sys.argv)<=1):
		print ("\nUsage: (install|add|remove|view|-v|--version) ... \n")
	else:
		for value in range(len(sys.argv)):
			if value != 0:
				sys.argv[value] = re.sub(r'[^-:/_a-zA-Z0-9.]', '', sys.argv[value])
			
		set_command()
		
	return 0

# Indicates what command we are using
def set_command():
	
	command = sys.argv[1]
	
	valid_commands = ['install', 'add', 'remove', 'view', '-v', '--version']
	
	if command == "":
		print("Valid commands: install, add, remove")
	elif command in valid_commands:
		if command == 'install':
			install()
		elif command == 'add':
			add()
		elif command == 'remove':
			remove()
		elif command == 'view':
			view()
		elif command == "--version" or command == "-v":
			show_version()
	else:
		print("Invalid command ")

def install():
	if len(sys.argv) < 4:
		error("Usage: \n    sll.py install <language> <library or framework name> [<version>]")
		exit (1)
	
	language_string = sys.argv[2]
	
	language = get_language(language_string)
	if language == False:
		error("Language not found")
		exit(1)
	
	library_string = sys.argv[3]
	library = get_library(language,library_string)
	if  library == False:
		error("Library not found")
		exit(1)

	
	if len(sys.argv) > 4:
		version_string = sys.argv[4]
	else:
		version_string = 'latest'
	
	link = get_download_link(library,version_string)
	
	if  link == False:
		error("Link not found")
		exit(1)
	
	name = library_string + "-" + version_string + "." + language_string
	print(name)
	
	download_file(link, name)
		
def add():
	if len(sys.argv) < 6:
		error("Usage: \n    sll.py add <language> <library or framework name> <version> <url> [latest]")
		exit (1)
	
	language = sys.argv[2]
	library = sys.argv[3]
	version = sys.argv[4]
	url = sys.argv[5]
	latest = False
	
	if len(sys.argv) >= 7:
		latest = True
		
		
	check = check_download_link(url)
	if check == False:
		error("Could not access the link, exiting.")
		exit(1)
	
	
	if not language in SOURCE_JSON:
		print("Adding new language, " + language)
		SOURCE_JSON[language] = {}
	
	if not library in SOURCE_JSON[language]:
		SOURCE_JSON[language][library] = {}
	
	if not version in SOURCE_JSON[language][library]:
		SOURCE_JSON[language][library][version] = url
	elif not latest == True and not 'latest' in SOURCE_JSON[language][library]:
		SOURCE_JSON[language][library]['latest'] = version
	else:
		error("This item already exists")
		exit(1) 
		
	
	SOURCE_FILE_WRITE = open(SOURCE_FILE_PATH, "w")
	print ("Updating to source file")
	SOURCE_FILE_WRITE.write(json.dumps(SOURCE_JSON, sort_keys=True, indent=4))
	SOURCE_FILE_WRITE.close()
	 
def remove():
	if len(sys.argv) < 3:
		error("Usage: \n    sll.py remove <language> [<library or framework name> [<version>]]]")
		exit (1)
	
	library = ""
	version = ""

	
	
	language = sys.argv[2]
	if len(sys.argv)  == 3:
		if language in SOURCE_JSON:
			print("Do you want you remove all of the language " + language + "?")
			value = input("(y,n)>")
			if value == "y":
				del SOURCE_JSON[language]
			else:
				print ("Not removing")
				exit(0)
		else:
			print("Language '" + language + "' does not exist")
			exit(0)	 
	if len(sys.argv) == 4:
		library = sys.argv[3]
		if language in SOURCE_JSON and library in SOURCE_JSON[language]:
			print("Do you want you remove all of the " + language + " library/framework " + library + "?")
			value = input("(y,n)>")
			if value == "y":
				del SOURCE_JSON[language][library]
			else:
				print ("Not removing")
				exit(0)
		else:
			print("The given library and/or language does not exist.")
			exit(0)
	if len(sys.argv) == 5:
		library = sys.argv[3]
		version = sys.argv[4]
		
		if language in SOURCE_JSON and library in SOURCE_JSON[language] and version in SOURCE_JSON[language][library]:
			print("Do you want you remove " + version + " of the " + language + " library/framework " + library + "?")
			value = input("(y,n)>")
			if value == "y":
				
				if version == "latest":
					del SOURCE_JSON[language][library][SOURCE_JSON[language][library]['latest']]
					del SOURCE_JSON[language][library]['latest']
				else:
					del SOURCE_JSON[language][library][version]
			else:
				print ("Not removing")
				exit(0)
		else:
			print("The given version, library and/or language does does not exist.")
			exit(0)
	 	

	
	
	SOURCE_FILE_WRITE = open(SOURCE_FILE_PATH , "w")
	print ("Updating source file")
	SOURCE_FILE_WRITE.write(json.dumps(SOURCE_JSON, sort_keys=True, indent=4))
	SOURCE_FILE_WRITE.close()
	
def view():
	for lang in SOURCE_JSON:
		
		if len(sys.argv) == 3 and sys.argv[2] != lang:
			continue
		language = get_language(lang)
		print("\n" + lang + "\n==============================")
		for lib in language:
			print ("\t" + lib + "\n\t--------------------")
			library = get_library(language,lib)
			for ver in library:
				print ("\t   " + ver + " => " + library[ver])
					
			print("\n")
	exit(0)
		
def get_language(lang):
	if lang in SOURCE_JSON:
		return SOURCE_JSON[lang]
	else:
		return False

def get_library(language,lib_name):
	if lib_name in language:
		return language[lib_name]
	else:
		return False
		
def get_download_link(lib, version):
	if version == 'latest':
		version = lib['latest']

	if version in lib:
		return lib[version]
	elif 'latest' in lib:
		return lib['latest']
	else:
		return False

def check_download_link(link):
	print(link)
	try:
		
		response = urllib.request.urlopen(link)
		code = response.getcode()
		print(code)
		if code == 200:
			return True
		else:
			False
	except urllib.error.HTTPError as e:
		print (e)
		return False
	except Exception as e:
		print (e)
		return False
	
def set_lib(json_string):
	global running_version
	global running_lib 
	
	lib = sys.argv[3]

	if lib in json_string:
		if len(sys.argv)==4:
			will_install = "latest"
		else:
			will_install = sys.argv[4]
		
		running_lib = lib
		
		print("\nWill install " + will_install)
		
		if will_install in json_string[lib]:
			if (will_install == "latest"):
				will_install = json_string[lib]["latest"]
				if not will_install in json_string[lib]:
					print("Version '" + will_install + "' for latest has not been added")
				else:
					running_version = will_install
					download_file(json_string[lib][will_install])
			else:
				running_version = will_install
				download_file(json_string[lib][will_install])
		else:
			print("No version '" + will_install + "' has been added")
		
		
		
	else:
		print("Invalid or unregistered library or framework " + lib)

def download_file(path, name):
	print("Downloading file, this may take awhile...")
	file_name, headers = urllib.request.urlretrieve(path)
	
	print("Placed in " + file_name)
	
	
	output = subprocess.check_output('file ' + file_name,shell=True)
	
	output = output.decode("utf-8")
	
	
	if "ASCII text" in output:
		try:
			print("Moving to " + os.getcwd())
			#print(os.getcwd())
			shutil.move(file_name, os.getcwd() + "/" + name)
			successful_install()
			
		except Error as e:
			print("Recived error: " + e.args[0])
	elif "Zip archive" in output:
		
		print("Found ZIP file, unzipping in currrent directory")
		print(os.getcwd())
		
		c_file = zipfile.ZipFile(file_name)
		for name in c_file.namelist():
			(dirname, filename) = os.path.split(name)
			
			if dirname == "":
				dirname = "./"
			if not os.path.exists(dirname):
				os.makedirs(dirname)
			c_file.extract(name, dirname)
		successful_install()
	elif "gzip compressed" in output:
		
		print("Found GZIP file, unzipping in currrent directory")
		print(os.getcwd())
		
		archive = tarfile.open(file_name, mode='r:gz')
		archive.extractall()
		successful_install()
	else:
		print(output)
	
def successful_install():
	print("\n\n! - Successfully installed\n\n")

def error(error_message):
	print("\n\n! - An error occured, install did not complete successfully.\n")
	print("Error Message: " + error_message + "\n\n")

def show_version():
	print ("\n\nSimple Little Loader v" +  VERSION + "\n")
	print ("Made by Jacob Hartman")
	print ("Licsensed under GPLv3\n\n")

main()

