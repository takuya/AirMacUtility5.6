﻿#! /usr/bin/pythonimport objc, os, sysfrom Foundation import *# get the arguments(scriptFile, pathToScriptFile, statusFilePath, bookTitle, serverBaseURL) = sys.argv[:5]# create semaphore file to communicate with JavaScript and set its initial valuewith open(statusFilePath, 'w') as statusFile:	statusFile.write("CHECKING_FOR_REDIRECT")	# path variablesdirectoryPath = os.path.expanduser("~/Library/Documentation/Help/%s/" % bookTitle)type_2_new_index_path = directoryPath + "index.html"type_3_new_index_path = directoryPath + "Contents/Resources/index.html"# if a suitable download already exists and we are not in that download, just return that to JavaScriptif -1 == pathToScriptFile.find("Library/Documentation"):	if os.path.isfile(type_2_new_index_path):		with open(statusFilePath, 'w') as statusFile:			statusFile.write(type_2_new_index_path)		exit()	elif os.path.isfile(type_3_new_index_path):		with open(statusFilePath, 'w') as statusFile:			statusFile.write(type_3_new_index_path)		exit()# if no file exists, update the semaphore so that JS can show the update graphicwith open(statusFilePath, 'w') as statusFile:	statusFile.write("CHECKING_FOR_UPDATE")# create the file managerfileManager = NSFileManager.defaultManager()# get the version number from the serverserverVersionURL = serverBaseURL + "helpbook-version.txt"serverVersion = NSString.stringWithContentsOfURL_encoding_error_(NSURL.URLWithString_(serverVersionURL), NSUTF8StringEncoding, None)serverVersion = serverVersion[0]# get the local version numberlocalVersionURL = directoryPath + "helpbook-version.txt"localVersion = NSString.stringWithContentsOfFile_encoding_error_(localVersionURL, NSUTF8StringEncoding, None)localVersion = localVersion[0]# show the help if we do have the latest helpif not serverVersion or serverVersion == localVersion:	with open(statusFilePath, 'w') as statusFile:		statusFile.write("NO_UPDATE_AVAILABLE")	exit()	# download the zip filezipDownloadPath = serverBaseURL + "helpbook.zip"zipData = NSData.dataWithContentsOfURL_(NSURL.URLWithString_(zipDownloadPath))if zipData:	# delete all of the contents of the folder, to make room for the new one	fileEnumerator = fileManager.enumeratorAtPath_(directoryPath)		if fileEnumerator:		while 1:			fileToDelete = fileEnumerator.nextObject()					if None == fileToDelete:				break					# delete the file			fileManager.removeItemAtPath_error_(directoryPath + fileToDelete, None)		# create the directory if it doesn't exist	fileManager.createDirectoryAtPath_withIntermediateDirectories_attributes_error_(directoryPath, True, None, None)		# write the data out to the right path	localZipPath = directoryPath + "downloadedfromserver.zip"	zipData.writeToFile_atomically_(localZipPath, True)		# unzip the package	os.system("/usr/bin/unzip '%s' -d '%s' 2>&1 1>/dev/null" % (localZipPath, directoryPath))		# remove the zip file	fileManager.removeItemAtPath_error_(localZipPath, None)		# save the version number locally	serverVersion.writeToFile_atomically_encoding_error_(localVersionURL, False, NSUTF8StringEncoding, None)		# import the HelpData framework	framework="/System/Library/PrivateFrameworks/HelpData.framework"	objc.loadBundle("HelpData", globals(), framework)		# check for a book that doesn't exist, which should register our book	HPDSearchManager.sharedSearchManager().bookWithIdentifier_("com.apple.apd.bookthatdoesntexist")		# stop and restart the helpd process	os.system("launchctl stop com.apple.helpd ; launchctl start com.apple.helpd")# figure out what we want to return to JavaScript: 2 means failure, filepath means successjs_return_value = "UPDATE_FAILURE"if os.path.isfile(type_2_new_index_path):	js_return_value = type_2_new_index_pathelif os.path.isfile(type_3_new_index_path):	js_return_value = type_3_new_index_path# tell JavaScript that we are donewith open(statusFilePath, 'w') as statusFile:	statusFile.write(js_return_value)