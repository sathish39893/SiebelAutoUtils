'''
	Import SIF files using import sif utility
Author: SATHISH PANTHAGANI

Inputs: sifDir : directory containing sif files
		logFile: log file of sif import utility

Outputs: objListFile : csv file containing objects 
		which are imported

'''
import os,sys,time
import re

#Get variable values from parameter file
def getVarFromFile(filename):
	global ToolsexePath,cfgPath,userName,passWord,dataSource,objListFile,sifFileDir,sifImportLog,subDirImport
	
	import configparser
	parser = configparser.ConfigParser(allow_no_value=True,inline_comment_prefixes=(';','#'))
	parser.read(filename)
	
	ToolsexePath = parser['sifImport']['ToolsexePath']
	cfgPath = parser['sifImport']['cfgPath']
	userName = parser['sifImport']['userName']
	passWord = parser['sifImport']['passWord']
	dataSource = parser['sifImport']['dataSource']

	objListFile,sifFileDir,sifImportLog = "","",""

	if parser.has_option('sifImport', 'objListFile'):objListFile = parser.get('sifImport','objListFile')
	if parser.has_option('sifImport', 'sifFileDir'):sifFileDir = parser.get('sifImport','sifFileDir')
	if parser.has_option('sifImport', 'sifImportLog'):sifImportLog = parser.get('sifImport','sifImportLog')
	if parser.has_option('sifImport', 'subDirImport'):subDirImport = parser.getboolean('sifImport','subDirImport')
	else:subDirImport=False

def validateInputs():
	global ToolsexePath,cfgPath,userName,passWord,dataSource,sifFileDir,sifImportLog
	if ToolsexePath != "" and os.path.exists(ToolsexePath.strip("\"").strip("\'")) is False:
		print('ToolsexePath: %s does not exist'%ToolsexePath)
		sys.exit()
	if cfgPath != "" and os.path.exists(cfgPath.strip("\"").strip("\'")) is False:
		print('cfgPath: %s does not exists'%cfgPath)
		sys.exit()
	if sifFileDir == "":
		print("please provide sifFileDir parameter")
		sys.exit()
	if sifFileDir != "" and os.path.exists(sifFileDir.strip("\"").strip("\'")) is False:
		print('sifFileDir: %s does not exists'%sifFileDir)
		sys.exit()
	if sifImportLog == "":
		print('please provide sifImportLog parameter')
		sys.exit()	
	
	print("%s: Validation of input parameters successful"%time.strftime("%d %b %Y %H:%M:%S",time.localtime()))

def importSIF(configFile):
	global ToolsexePath,cfgPath,userName,passWord,dataSource,sifFileDir,sifImportLog,subDirImport
	sDirFile = ""
	getVarFromFile(configFile)
	validateInputs()
	cmd = ToolsexePath+" /c "+cfgPath+" /u "+userName+" /p "+passWord+" /d "+dataSource+" /batchimport 'Siebel Repository' merge "+sifFileDir+" "+sifImportLog
	
	if os.path.isdir(sifFileDir.strip("\"").strip("\'")):
		sDirFile = "directory"
		arrFiles = [f for f in os.listdir(sifFileDir.strip("\"").strip("\'")) if f.lower().endswith('.sif')] #verify if sif files are present in directory
		#if sifImportLog =="":sifImportLog = sifFileDir+"\\sifImport.log"
		if len(arrFiles) == 0:
			print("%s: no SIF files found in directory: %s"%(time.strftime("%d %b %Y %H:%M:%S",time.localtime()),sifFileDir))
		else:
			print("%s: SIF file import started from %s: %s, logfile: %s"%(time.strftime("%d %b %Y %H:%M:%S",time.localtime()),sDirFile,sifFileDir,sifImportLog))	
			os.system(cmd)
			parseImportLog(sifImportLog,objListFile,'false')
		#import files from sub directory
		if subDirImport == True:
			for entry in os.scandir(sifFileDir.strip("\"").strip("\'")):
				if not (entry.name.startswith('.') or entry.name.startswith('__')) and entry.is_dir():
					sifFileDirSub = '"'+os.path.join(sifFileDir.strip("\"").strip("\'"),entry.name)+'"' # need to add quotes to make siebel tools to work
					print("%s: SIF file import started from %s: %s, logfile: %s"%(time.strftime("%d %b %Y %H:%M:%S",time.localtime()),sDirFile,sifFileDirSub,sifImportLog))	
					cmd = ToolsexePath+" /c "+cfgPath+" /u "+userName+" /p "+passWord+" /d "+dataSource+" /batchimport 'Siebel Repository' merge "+sifFileDirSub+" "+sifImportLog
					os.system(cmd)
					parseImportLog(sifImportLog,objListFile,'true')
	elif os.path.isfile(sifFileDir.strip("\"").strip("\'")): 
		sDirFile = "file"
		print("%s: SIF file import started from %s: %s, logfile: %s"%(time.strftime("%d %b %Y %H:%M:%S",time.localtime()),sDirFile,sifFileDir,sifImportLog))	
		os.system(cmd)
		parseImportLog(sifImportLog,objListFile,'false')
	else: pass
	print("%s: SIF file import done."%(time.strftime("%d %b %Y %H:%M:%S",time.localtime())))

def parseImportLog(sifImportLog,objListFile,appendfile='false'):
	sifFileList = []
	Objlist = []
	Prevline = ""
	if objListFile == "": return None
	
	for line in open(sifImportLog.strip("\"").strip("\'")):
		#Importing objects from file C:\Users\sathish.panthagani\Desktop\Siebel\SIF\Object1.sif"
		pattern2 =  "Done loading (.*?$)"
		m2 = re.search(pattern2,line)
		if m2 is not None:
			sifFileName = m2.group(1)
			sifFileList.append(sifFileName)
			
		#Text found in log file
		#Loading Applet ' Contact Quota Period List Applet' ... found
		pattern = "Loading (.*?) \'(.*)\'(.*?) ... found"
		m = re.search(pattern,line)
		if m is not None:
			if m.group(1) not in ('Project','Repository'):
				ObjType = m.group(1)
				ObjName = m.group(2)
				Objlist.append(ObjType+","+ObjName)
		
		#STATUS: Total Files: 36, Successful Imports: 33, Failed Imports: 3
		pattern1 = "STATUS: Total Files: ([0-9]+), Successful Imports: ([0-9]+), Failed Imports: ([0-9]+)"
		m1 = re.search(pattern1,line)
		if m1 is not None:
			TotalFilesCount = m1.group(1)
			SuccessImportCount = m1.group(2)
			FailedImportCount = m1.group(3)
		
		# To retrieve the project name
		#Loading Project 'ADM Test' ... found
		#Loading Project 'ADM Test' ... and Applet children
		if Prevline is not None:
			pattern3 = "Loading Project \'(.*)\' ... found"
			pattern4 = "Loading Project \'(.*)\' ... and Applet children"
			if re.search(pattern3,Prevline) is not None and re.search(pattern4,line) is not None:
				m4 = re.search(pattern4,line)
				ObjName = m4.group(1)
				Objlist.append("Project,"+ObjName)
		Prevline = line # reassign the new line
	#print(sifFileList)
	#write to a csv file
	filemode = "w"
	if len(Objlist) > 0 and objListFile != "": 
		if appendfile == 'true': filemode = "a+"
		with open(objListFile.strip("\"").strip("\'"),filemode) as f:
			if filemode == "a+" and f.tell() > 2:f.write("\n") # add new line only when the file has content
			f.writelines("\n".join(Objlist))
		if appendfile == 'true': print("%s: Object list file updated: %s"%(time.strftime("%d %b %Y %H:%M:%S",time.localtime()),objListFile))
		else: print("%s: Object list file created: %s"%(time.strftime("%d %b %Y %H:%M:%S",time.localtime()),objListFile))
def main():
	print("*"*60+"\n\n\tImport sif files to Siebel Tools\n\t\tversion: 1.0\n\n"+"*"*60)

	if len(sys.argv) < 2:
		print("Usage: %s configfile \nexample: %s configfile.ini"%(sys.argv[0],sys.argv[0]))
		sys.exit()
	else:
		configFile = sys.argv[1]
	importSIF(configFile)
if __name__ == "__main__":
	main()