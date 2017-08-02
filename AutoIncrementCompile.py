'''
Auto Incremental Compilation for Siebel Tools

Author: SATHISH PANTHAGANI
Inputs: Tools Path, SRF File Path, Object List File

Outputs: Compilation Object to SRF File

'''

from pywinauto.application import Application
import os,sys,time

print("*"*60+"\n\n\tAuto Incremental Compilation for Siebel Tools\n\t\tversion: 1.2\n\n"+"*"*60)

if len(sys.argv) < 2:
	print("Usage: %s configfile \nexample: python %s AutoIncrementCompile_params.txt"%(sys.argv[0],sys.argv[0]))
	sys.exit()
else:
	configFile = sys.argv[1]

#Get variable values from parameter file
def getVarFromFile(filename):
    import imp
    f = open(filename)
    global data
    data = imp.load_source('data', '', f)
    f.close()
getVarFromFile(configFile)

ToolsWinTitle = data.ToolsWinTitle  # 'Siebel Tools - Siebel Repository'
ToolsexePath = data.ToolsexePath #r"C:\Siebel\15.0.0.0.0\Tools\BIN\siebdev.exe"
cfgPath = data.cfgPath #r'c:\Siebel\15.0.0.0.0\Tools\bin\enu\tools.cfg'
userName = data.userName #"SPANTH"
passWord = data.passWord #"SPANTH"
dataSource = data.dataSource #"Local"
srfFile = data.srfFile #r"C:\Siebel\15.0.0.0.0\Client\OBJECTS\enu\siebel_sia_auto.srf"
objListFile = data.objListFile #r"C:\Users\sathish.panthagani\Documents\Python Scripts\SiebelObjectList.txt"

if hasattr(data, 'ToolsLaunchTimeOut'): 
	ToolsLaunchTimeOut = data.ToolsLaunchTimeOut
else:
	ToolsLaunchTimeOut = 1000 #default if not exist in param file

ToolsPath = ToolsexePath+" /c "+cfgPath+" /u "+userName+" /p "+passWord+" /d "+dataSource
#print(ToolsLaunchTimeOut)

def validateInputs():
	if os.path.exists(ToolsexePath) is False:
		print('ToolsexePath: %s does not exist'%ToolsexePath)
		sys.exit()
	if os.path.exists(cfgPath) is False:
		print('cfgPath: %s does not exists'%cfgPath)
		sys.exit()
	if os.path.exists(srfFile) is False:
		print('srfFile: %s does not exist'%srfFile)
		sys.exit()
	if os.path.exists(objListFile) is False:
		print('objListFile: %s does not exist'%objListFile)
		sys.exit()
	print("%s: Validation successful"%time.strftime("%d %b %Y %H:%M:%S",time.localtime()))

#Validate inputs provided in file
validateInputs()

#Launch Tools
print("%s: Siebel Tools started.."%time.strftime("%d %b %Y %H:%M:%S",time.localtime()))
app = Application().start(ToolsPath,timeout=ToolsLaunchTimeOut)
app = Application().connect(path=ToolsexePath)
app[ToolsWinTitle].wait("exists enabled visible ready")

dlg = app.top_window() #dlg = app['Siebel Tools - Siebel Repository']
dlg.type_keys("^E") # to open Object Explorer
objexpl = app.SiebelToolsSiebelRepository.ObjectExplorer1.TreeView.WrapperObject() #Object explorer window

#Open Object Compile Window and compile
def compileObj(ObjType, ObjName):
	if ObjType == "Project":
		app[ToolsWinTitle].type_keys("{F7}") #Opens Compilation Window
		app['Object Compiler']['Siebel repository file:Edit'].set_edit_text(srfFile) #SRF File location
		app['Object Compiler']['ListBox'].Select(ObjName, select=True)
		app['Object Compiler']['Compile'].click()
		print("%s: Compiling Project:%s\tType:%s"%(time.strftime("%d %b %Y %H:%M:%S",time.localtime()),ObjName,ObjType))
	else:
		app[ToolsWinTitle].type_keys("^{F7}") #Opens Compilation Window
		if app['Object Compiler'].exists(1):
			app['Object Compiler']['Siebel repository file:Edit'].set_edit_text(srfFile) #SRF File location
			ObjCount = app['Object Compiler']['ListBox'].item_count()
			if ObjCount == 1:
				ObjList = app['Object Compiler']['ListBox'].item_texts()
				if ObjList[0] == ObjName: # verify the object name is matched
					app['Object Compiler']['Compile'].click()  #Compilation Starts
					print("%s: Compiling ObjectType:%s\tName:%s"%(time.strftime("%d %b %Y %H:%M:%S",time.localtime()),ObjType,ObjName))
					errMsg = ""
					if app['Error'].exists():
						errMsg = app['Error']['ErrorEdit'].TextBlock()
						app['Error']['OK'].click()
						if(errMsg):
							print(errMsg)
					else:
						pass
				else:
					print("%s: Compilation failed for ObjectType:%s\tName:%s"%(time.strftime("%d %b %Y %H:%M:%S",time.localtime()),ObjType,ObjName))
					app['Object Compiler']['Cancel'].click() # cancel compile
			else:
				print("%s: Multiple Objects found in Compile Window:ObjectType:%s\tName:%s"%(time.strftime("%d %b %Y %H:%M:%S",time.localtime()),ObjType,ObjName))
			#app['Object Compiler']['Compile'].wait_not('visible') #not required
		else:
			print("%s: Compilation failed for ObjectType:%s\tName:%s"%(time.strftime("%d %b %Y %H:%M:%S",time.localtime()),ObjType,ObjName))

#Query for the compile Objects
def QuerynCompileObjects(ObjType, ObjName):
	sEditCtrl = "~"+ObjType+"sEdit" #Object Plural Form is used for this window
	sTreeObjPath = '\\Siebel Objects\\'+ObjType
	targetobj = objexpl.get_item(sTreeObjPath).click() #click on object explorer items
	
	app[ToolsWinTitle][sEditCtrl].wait('visible') # It will wait till the window appears
	ObjNameTemp = "'"+ObjName+"'" # added quotes to avoid query errors
	dlg.type_keys("^Q") # Query for the object Name

	app[ToolsWinTitle][sEditCtrl].set_edit_text(ObjNameTemp)
	dlg.type_keys("^{ENTER}")

	#dlg.type_keys("+{VK_DOWN 2}")
	compileObj(ObjType, ObjName) # Compiles Object
	

print("%s: Compilation Started..."%time.strftime("%d %b %Y %H:%M:%S",time.localtime()))
#siebObjType = "Business Component"
#siebObjName = "ABO Bulk Request Actions*"

#added below to avoid typo errors
ObjectList = {	'Bitmap Category':['BITMAP CATEGORY','BITMAP'],
				'Business Component':['BUSINESS COMPONENT','BC', 'BUSCOMP'],
				'Business Object':['BUSINESS OBJECT','BO'], 
				'Business Service':['BUSINESS SERVICE','BS'],
				'Class':['CLASS'],
				'Command':['COMMAND'],
				'Find':['FIND'],
				'HTML Heirarchy Bitmap':['HTML HEIRARCHY BITMAP'],
				'Help Id':['HELP ID'],
				'Icon Map':['ICON MAP','ICON'],
				'Integration Object':['INTEGRATION OBJECT','IO','INT OBJ'],
				'Application':['APPLICATION','APP','APPL'],
				'Applet':['APPLET'],  #application and applet needs to be same sequence
				'Link':['LINK'],
				'Menu':['MENU'],
				'Message Category':['MESSAGE CATEGORY'],
				'Pick List':['PICK LIST'],
				'Project':['PROJECT'],
				'Screen':['SCREEN'],
				'Symbolic String':['SYMBOLIC STRING'],
				'Table':['TABLE'],
				'Task Group':['TASK GROUP'],
				'Toolbar':['TOOLBAR'],
				'Type':['TYPE'],
				'View':['VIEW'],
				'Web Page':['WEB PAGE'],
				'Web Template':['WEB TEMPLATE','WEB TEMPL','WEBTEMPL'],
				'Import Object':['IMPORT OBJECT']
			}
def searchObjType(searchFor):
	for k in ObjectList:
		if k == searchFor:
			return k
		else:
			for v in ObjectList[k]:
				if searchFor.upper() in v:
					return k
	return None

#dict holds the lines from objListFile
dict = {}
for line in open(objListFile):
	linelist = line.split(",")
	if len(linelist) < 3:
		siebObjType = linelist[0].strip()
		siebObjName = linelist[1].strip()
		dict[siebObjName] = siebObjType  #adding to dictionary to remove duplicate objects
#print(dict.items())

for key in dict:
	newObjType = searchObjType(dict[key])
	if newObjType is not None:
		QuerynCompileObjects(newObjType,key)  #siebObjType,siebObjName
	else:
		print("%s: Siebel Object Type %s is not found/not supported..."%(time.strftime("%d %b %Y %H:%M:%S",time.localtime()),dict[key]))

print("%s: Compilation End..."%time.strftime("%d %b %Y %H:%M:%S",time.localtime()))

# Close/exit Siebel Tools
dlg.close_alt_f4()
print("%s: Siebel Tools closed.."%time.strftime("%d %b %Y %H:%M:%S",time.localtime()))
