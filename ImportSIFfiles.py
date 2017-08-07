'''

Author: SATHISH PANTHAGANI
email: sathish.panthagani@accenture.com
Inputs: 

Outputs: 

'''
import os,sys
import re

logFile = "C:\\Users\\sathish.panthagani\\Desktop\\Siebel\\import.log"
sifDir = r'C:\Users\sathish.panthagani\Desktop\Siebel\SIF'
#cmd = r"C:\Siebel\15.0.0.0.0\Tools\BIN\siebdev.exe /c 'c:\Siebel\15.0.0.0.0\Tools\bin\enu\tools.cfg' /u SPANTH /p SPANTH /d local /batchimport 'Siebel Repository' merge 'C:\Users\sathish.panthagani\Desktop\Siebel\SIF' 'C:\Users\sathish.panthagani\Desktop\Siebel\import.log'"
#os.system(cmd)

sifFileList = []
Objlist = []
Prevline = ""

arrFiles = os.listdir(sifDir)
print(arrFiles)
if len(arrFiles) == 0:
	print('Hello')
sys.exit()


for line in open(logFile):

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
if Objlist is not None:
	with open("test.csv","w") as f:
		f.writelines("\n".join(Objlist))
	