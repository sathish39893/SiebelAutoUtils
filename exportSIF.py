'''
	export sif files from the objectlist file from siebel tools 
	Author: SATHISH PANTHAGANI
	
	Inputs: objectlistexport : file containing the list of object to be exported
			logFile : export log file name

	Outputs: list of sif files exported to the directory mentioned

'''
import os,sys,time
import re

#Get variable values from parameter file
def getVarFromFile(filename):
	global ToolsexePath,cfgPath,userName,passWord,dataSource,sifExpObjlistFile,sifExportLog
	sifExpObjlistFile,sifExportLog = "",""
	import configparser
	parser = configparser.ConfigParser(allow_no_value=True,inline_comment_prefixes=(';','#'))
	parser.read(filename)
	
	ToolsexePath = parser.get('sifExport','ToolsexePath')
	cfgPath = parser['sifExport']['cfgPath'] 
	userName = parser['sifExport']['userName'] 
	passWord = parser['sifExport']['passWord']
	dataSource = parser['sifExport']['dataSource'] 

	if parser.has_option('sifExport', 'sifExpObjlistFile'):sifExpObjlistFile = parser['sifExport']['sifExpObjlistFile']
	if parser.has_option('sifExport', 'sifExportLog'):sifExportLog = parser['sifExport']['sifExportLog']

def validateInputs():
	global ToolsexePath,cfgPath,userName,passWord,dataSource,sifExpObjlistFile,sifExportLog
	if ToolsexePath != "" and os.path.exists(ToolsexePath.strip("\"").strip("\'")) is False:
		print('ToolsexePath: %s does not exist'%ToolsexePath)
		sys.exit()
	if cfgPath != "" and os.path.exists(cfgPath.strip("\"").strip("\'")) is False:
		print('cfgPath: %s does not exists'%cfgPath)
		sys.exit()
	if sifExpObjlistFile == "":
		print("please provide sifExpObjlistFile parameter")
		sys.exit()
	if sifExpObjlistFile != "" and os.path.exists(sifExpObjlistFile.strip("\"").strip("\'")) is False:
		print('sifExpObjlistFile: %s does not exists'%sifExpObjlistFile)
		sys.exit()
	
	print("%s: Validation of input parameters successful"%time.strftime("%d %b %Y %H:%M:%S",time.localtime()))

def exportSIF(configFile):
	global ToolsexePath,cfgPath,userName,passWord,dataSource,sifExpObjlistFile,sifExportLog
	getVarFromFile(configFile)
	validateInputs()
	#if sifExportLog =="":sifExportLog = sifDir+"\\sifImport.log"
	print("%s: SIF file export started from file: %s, logfile: %s"%(time.strftime("%d %b %Y %H:%M:%S",time.localtime()),sifExpObjlistFile,sifExportLog))
	cmd = ToolsexePath+" /c "+cfgPath+" /u "+userName+" /p "+passWord+" /d "+dataSource+" /batchexport 'Siebel Repository' "+sifExpObjlistFile+" "+sifExportLog
	os.system(cmd)
	print("%s: SIF file export done."%(time.strftime("%d %b %Y %H:%M:%S",time.localtime())))

	sifFileList = []
	Objlist = []
	Prevline = ""
	for line in open(sifExportLog.strip("\"").strip("\'")):
		#Importing objects from file C:\Users\sathish.panthagani\Desktop\Siebel\SIF\Object1.sif"
		pattern2 =  "Exporting objects to file (.*?$)"
		m2 = re.search(pattern2,line)
		if m2 is not None:
			sifFileName = m2.group(1)
			sifFileList.append(sifFileName)
			
		#Text found in log file
		#Loading Business Component 'Account' ... found
		pattern = "Loading (.*?) \'(.*)\'(.*?) ... found"
		m = re.search(pattern,line)
		if m is not None:
			if m.group(1) not in ('Project','Repository'):
				ObjType = m.group(1)
				ObjName = m.group(2)
				Objlist.append(ObjType+","+ObjName)
		
		#STATUS: Total: 1, Successful Exports: 1, Failed Exports: 0
		pattern1 = "STATUS: Total: ([0-9]+), Successful Exports: ([0-9]+), Failed Exports: ([0-9]+)"
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

def main():
	print("*"*60+"\n\n\texport sif files from Siebel Tools\n\t\tversion: 1.0\n\n"+"*"*60)

	if len(sys.argv) < 2:
		print("Usage: %s configfile \nexample: %s configfile.ini"%(sys.argv[0],sys.argv[0]))
		sys.exit()
	else:
		configFile = sys.argv[1]

	exportSIF(configFile)
if __name__ == "__main__":
	main()