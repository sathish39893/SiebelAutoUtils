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
	global ToolsexePath,cfgPath,userName,passWord,dataSource,objListFile,sifFileDir,sifImportLog
	
	import configparser
	parser = configparser.ConfigParser(allow_no_value=True,inline_comment_prefixes=(';','#'))
	parser.read(filename)
	
	ToolsWinTitle = parser['Internal']['ToolsWinTitle'] # data.ToolsWinTitle
	ToolsexePath = parser['sifImport']['ToolsexePath'] # data.ToolsexePath #r"C:\Siebel\15.0.0.0.0\Tools\BIN\siebdev.exe"
	cfgPath = parser['sifImport']['cfgPath'] #data.cfgPath #r'c:\Siebel\15.0.0.0.0\Tools\bin\enu\tools.cfg'
	userName = parser['sifImport']['userName'] #data.userName #"SPANTH"
	passWord = parser['sifImport']['passWord']#data.passWord #"SPANTH"
	dataSource = parser['sifImport']['dataSource'] #data.dataSource #"Local"

	objListFile,sifFileDir,sifImportLog = "","",""

	if parser.has_option('sifImport', 'objListFile'):objListFile = parser['sifImport']['objListFile']
	if parser.has_option('sifImport', 'sifFileDir'):sifFileDir = parser['sifImport']['sifFileDir']
	if parser.has_option('sifImport', 'sifImportLog'):sifImportLog = parser['sifImport']['sifImportLog']

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
	
	print("%s: Validation of input parameters successful"%time.strftime("%d %b %Y %H:%M:%S",time.localtime()))

def importSIF(configFile):
	global ToolsexePath,cfgPath,userName,passWord,dataSource,sifFileDir,sifImportLog
	sifFileList = []
	Objlist = []
	Prevline = ""
	sDirFile = ""
	getVarFromFile(configFile)
	validateInputs()
	
	if sifFileDir =="":return None
	if sifImportLog =="":sifImportLog = sifFileDir+"\\sifImport.log"
	if os.path.isdir(sifFileDir):
		sDirFile = "directory"
		arrFiles = os.listdir(sifFileDir.strip("\"").strip("\'"))
		if len(arrFiles) == 0:
			print("%s: no SIF files found in directory: %s"%(time.strftime("%d %b %Y %H:%M:%S",time.localtime()),sifFileDir))
			sys.exit()
	elif os.path.isfile(sifImportLog.strip("\"").strip("\'")): sDirFile = "file"
	else: pass
	
	print("%s: SIF file import started from %s: %s, logfile: %s"%(time.strftime("%d %b %Y %H:%M:%S",time.localtime()),sDirFile,sifFileDir,sifImportLog))
	#Import SIF Files from the directory
	cmd = ToolsexePath+" /c "+cfgPath+" /u "+userName+" /p "+passWord+" /d "+dataSource+" /batchimport 'Siebel Repository' merge "+sifFileDir+" "+sifImportLog
	os.system(cmd)
	print("%s: SIF file import done."%(time.strftime("%d %b %Y %H:%M:%S",time.localtime())))
	
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
	if Objlist is not None and objListFile != "":
		with open(objListFile.strip("\"").strip("\'"),"w") as f:
			f.writelines("\n".join(Objlist))
		print("%s: Object list file created: %s"%(time.strftime("%d %b %Y %H:%M:%S",time.localtime()),objListFile))

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