'''
Auto Incremental Compilation for Siebel Tools

Author: SATHISH PANTHAGANI
email: sathish.panthagani@accenture.com
Inputs: Tools Path, SRF File Path, Object List File

Outputs: Compilation Objects to SRF File

'''

from pywinauto.application import Application
import pywinauto.timings as pywintime
import pywinauto.base_wrapper as basewrapper
import os,sys,time,re

errCount = 0
successCount = 0

#Get variable values from parameter file
def getVarFromFile(filename):
	global ToolsexePath,ToolsWinTitle,cfgPath,userName,passWord,dataSource,objListFile,srfFile,ToolsLaunchTimeOut,PopupTimeOut,ToolsPath
	
	import configparser
	parser = configparser.ConfigParser(allow_no_value=True,inline_comment_prefixes=(';','#'))
	parser.read(filename)
	
	ToolsWinTitle = parser['Internal']['ToolsWinTitle']
	ToolsexePath = parser['IncrCompile']['ToolsexePath'] 
	cfgPath = parser['IncrCompile']['cfgPath'] 
	userName = parser['IncrCompile']['userName'] 
	passWord = parser['IncrCompile']['passWord']
	dataSource = parser['IncrCompile']['dataSource'] 
	objListFile,srfFile,language = "","","enu"

	if parser.has_option('IncrCompile', 'objListFile'):objListFile = parser['IncrCompile']['objListFile']
	if parser.has_option('IncrCompile', 'srfFile'):srfFile = parser['IncrCompile']['srfFile']
	if parser.has_option('IncrCompile', 'language'):language = parser['IncrCompile']['language']

	if parser.has_option('Internal', 'ToolsLaunchTimeOut'):
		ToolsLaunchTimeOut = parser.getint('Internal','ToolsLaunchTimeOut')
	else:
		ToolsLaunchTimeOut = 1000 #default if not exist in param file

	if parser.has_option('Internal', 'PopupTimeOut'): 
		PopupTimeOut =  parser.getint('Internal','PopupTimeOut')
	else:
		PopupTimeOut = 1  # default value if parameter does not exist

	ToolsPath = ToolsexePath+" /c "+cfgPath+" /u "+userName+" /p "+passWord+" /d "+dataSource+" /l "+language
	#print(ToolsLaunchTimeOut)
	
	if parser.has_option('Internal', 'LoadTime'):
		if parser.get('Internal', 'LoadTime').upper() == 'SLOW': pywintime.Timings.Slow()
		elif parser.get('Internal', 'LoadTime').upper() == 'FAST': pywintime.Timings.Fast()
		else: pywintime.Timings.Defaults()
	else:
		pywintime.Timings.Defaults()

	if parser.has_option('Internal', 'ToolsWinTitle') and ToolsWinTitle =="":
		ToolsWinTitle = 'Siebel Tools - Siebel Repository'

def validateInputs():
	global ToolsexePath,ToolsWinTitle,cfgPath,userName,passWord,dataSource,objListFile,srfFile,ToolsLaunchTimeOut,PopupTimeOut,ToolsPath

	if ToolsexePath != "" and os.path.exists(ToolsexePath.strip("\"").strip("\'")) is False:
		print('ToolsexePath: %s does not exist'%ToolsexePath)
		sys.exit()
	if cfgPath != "" and os.path.exists(cfgPath.strip("\"").strip("\'")) is False:
		print('cfgPath: %s does not exists'%cfgPath)
		sys.exit()
	if srfFile =="":
		print("srfFile parameter cannot be blank")
		sys.exit()
	if srfFile !="" and os.path.exists(srfFile.strip("\"").strip("\'")) is False:
		print('srfFile: %s does not exist'%srfFile)
		sys.exit()
	if objListFile == "":
		print("objListFile parameter cannot be blank")
		sys.exit()
	if os.path.exists(objListFile.strip("\"").strip("\'")) is False:
		print('objListFile: %s does not exist'%objListFile)
		sys.exit()
	print("%s: Validation of input parameters successful"%time.strftime("%d %b %Y %H:%M:%S",time.localtime()))

#-------------------------Launch Tools for Incremental Compile -----------------------------#
def launchTools():
	global dlg,app,objexpl
	
	try:
		print("%s: Siebel Tools started.."%time.strftime("%d %b %Y %H:%M:%S",time.localtime()))
		app = Application().start(ToolsPath,timeout=ToolsLaunchTimeOut)
		#app = Application().connect(path=ToolsexePath)
		app[ToolsWinTitle].wait("exists enabled visible ready")
	except pywintime.TimeoutError as e:
		print("%s: timed out while launching Siebel Tools"%time.strftime("%d %b %Y %H:%M:%S",time.localtime()))
		raise e
	except:
		print("%s: error occured while launching Siebel Tools:"%time.strftime("%d %b %Y %H:%M:%S",time.localtime()))

	dlg = app.top_window() #dlg = app['Siebel Tools - Siebel Repository']
	dlg.type_keys("^E") # to open Object Explorer
	objexpl = app.SiebelToolsSiebelRepository.ObjectExplorer1.TreeView.WrapperObject() #Object explorer window
	#dlg.minimize()

#####Open Object Compile Window and compile
def compileObj(ObjType, ObjName):
	global successCount,errCount,dlg,app,objexpl
	errMsg,tmpErrMsg = "",""

	if ObjType == "Project":
		app[ToolsWinTitle].type_keys("{F7}") #Opens Compilation Window
		app['Object Compiler']['Siebel repository file:Edit'].set_edit_text(srfFile) #SRF File location
		app['Object Compiler']['ListBox'].Select(ObjName, select=True)
		app['Object Compiler']['Compile'].click()
		while app['Object Compiler'].exists(1):
			if app['Error'].exists(timeout=PopupTimeOut,retry_interval=1):
				tmpErrMsg = app['Error']['ErrorEdit'].TextBlock()
				app['Error']['OK'].click()
				if(tmpErrMsg):
					print("%s: Compilation failed: Exception occured: ObjectType: %s\tName: %s"%(time.strftime("%d %b %Y %H:%M:%S",time.localtime()),ObjType,ObjName))
					print(tmpErrMsg)
					errCount += 1
					errMsg = "ERRORPOP"
			else:
				pass
	else:
		app[ToolsWinTitle].type_keys("^{F7}") #Opens Compilation Window
		if app['Object Compiler'].exists(1):
			app['Object Compiler']['Siebel repository file:Edit'].set_edit_text(srfFile) #SRF File location
			ObjCount = app['Object Compiler']['ListBox'].item_count()
			if ObjCount == 1:
				ObjList = app['Object Compiler']['ListBox'].item_texts()
				if ObjList[0] == ObjName: # verify the object name is matched

					app['Object Compiler']['Compile'].click()  #Compilation Starts
					while app['Object Compiler'].exists():  # added not to get timeout
						if app['Error'].exists(timeout=PopupTimeOut,retry_interval=1):
							tmpErrMsg = app['Error']['ErrorEdit'].TextBlock()
							app['Error']['OK'].click()
							if(tmpErrMsg):
								print("%s: Compilation failed: Exception occured: ObjectType: %s\tName: %s"%(time.strftime("%d %b %Y %H:%M:%S",time.localtime()),ObjType,ObjName))
								print(tmpErrMsg)
								errCount += 1
								errMsg = "ERRORPOP"
						else:
							pass
				else:
					app['Object Compiler']['Cancel'].click() # cancel compile
					errMsg = "OBJNAMEMISMATCH"
			else:
				errMsg = "MULTI"
			#app['Object Compiler']['Compile'].wait_not('exists') #not required
		else:
			errMsg = "NOTFOUND"
	return errMsg

######Query for the compile Objects
def QuerynCompileObjects(ObjType, ObjName):
	global successCount,errCount,dlg,app,objexpl
	
	sEditCtrl = "~"+ObjType+"sEdit" #Object Plural Form is used for this window
	#sEditCtrl = ObjType+"sEdit" #Object Plural Form is used for this window
	#print(sEditCtrl)
	sTreeObjPath = '\\Siebel Objects\\'+ObjType
	targetobj = objexpl.get_item(sTreeObjPath).click() #click on object explorer items
	
	app[ToolsWinTitle][sEditCtrl].wait('visible exists active') # It will wait till the window appears
	ObjNameTemp = "'"+ObjName+"'" # added quotes to avoid query errors
	dlg.type_keys("^Q") # Query for the object Name

	app[ToolsWinTitle][sEditCtrl].set_edit_text(ObjNameTemp)
	dlg.type_keys("^{ENTER}")

	#dlg.type_keys("+{VK_DOWN 2}")
	return compileObj(ObjType, ObjName) # Compiles Object
#########	


def searchObjType(searchFor):
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
	for k in ObjectList:
		if k == searchFor:
			return k
		else:
			for v in ObjectList[k]:
				if searchFor.upper() in v:
					return k
	return None

def autoCompile(configFile):
	global successCount,errCount,dlg,app,objexpl
	getVarFromFile(configFile)
	validateInputs()
	#Validate inputs provided in file
	launchTools()
	print("%s: Compilation started..."%time.strftime("%d %b %Y %H:%M:%S",time.localtime()))
	for line in open(objListFile):
		linelist = line.split(",")
		if len(linelist) < 3:
			siebObjType = linelist[0].strip()
			siebObjName = linelist[1].strip()
		try:
			newObjType = searchObjType(siebObjType)	
			if newObjType is not None:
				errorMsg = QuerynCompileObjects(newObjType,siebObjName)  #siebObjType,siebObjName
				prevObjType = newObjType
				prevObjName = siebObjName
				if errorMsg == "":
					print("%s: Compilation successful: ObjectType: %s\tName: %s"%(time.strftime("%d %b %Y %H:%M:%S",time.localtime()),newObjType,siebObjName))
					successCount += 1
				elif errorMsg == "MULTI":
					print("%s: Compilation failed: Multiple Objects found in Compile Window: ObjectType: %s\tName: %s"%(time.strftime("%d %b %Y %H:%M:%S",time.localtime()),newObjType,siebObjName))
					errCount += 1
				elif errorMsg == "NOTFOUND":
					print("%s: Compilation failed: Object not found: ObjectType: %s\tName: %s"%(time.strftime("%d %b %Y %H:%M:%S",time.localtime()),newObjType,siebObjName))
					errCount += 1
				elif errorMsg == "OBJNAMEMISMATCH":
					print("%s: Compilation failed: Object Name mismatch: ObjectType: %s\tName: %s"%(time.strftime("%d %b %Y %H:%M:%S",time.localtime()),newObjType,siebObjName))
					errCount += 1	
				
			else:
				print("%s: Compilation failed: ObjectType not supported: ObjectType: %s\tName: %s"%(time.strftime("%d %b %Y %H:%M:%S",time.localtime()),siebObjType,siebObjName))
				errCount += 1		
			
		except basewrapper.ElementNotEnabled:
			print("%s: Compilation failed: Exception Occured: ObjectType:%s\tName:%s"%(time.strftime("%d %b %Y %H:%M:%S",time.localtime()),prevObjType,prevObjName))
			errCount += 1
			tmpErrMsg = ""
			if app['Error'].exists(timeout=PopupTimeOut,retry_interval=1):
				tmpErrMsg = app['Error']['ErrorEdit'].TextBlock()
				app['Error']['OK'].click()
				if(tmpErrMsg):
					print(tmpErrMsg)
			else:
				pass
		except pywintime.TimeoutError:
			print("%s: Compilation failed: TimeoutError Occured: ObjectType:%s\tName:%s"%(time.strftime("%d %b %Y %H:%M:%S",time.localtime()),newObjType,siebObjName))
			break   # might be an issue and needs to stop execution
		except IndexError:
			print("%s: Compilation failed: ObjectType is not enabled in Object Explorer: ObjectType:%s\tName:%s"%(time.strftime("%d %b %Y %H:%M:%S",time.localtime()),newObjType,siebObjName))
			errCount += 1
		except AttributeError:
			print("%s: Compilation failed: first column (i.e., Name) and should be editable in Query Mode: ObjectType:%s\tName:%s"%(time.strftime("%d %b %Y %H:%M:%S",time.localtime()),newObjType,siebObjName))
			errCount += 1		

	print("%s: Compilation done..."%time.strftime("%d %b %Y %H:%M:%S",time.localtime()))
	print("%s: Total Number of Objects compiled:%s"%(time.strftime("%d %b %Y %H:%M:%S",time.localtime()),successCount))
	print("%s: Total Number of Objects failed:%s"%(time.strftime("%d %b %Y %H:%M:%S",time.localtime()),errCount))
	# Close/exit Siebel Tools
	try:
		dlg.close_alt_f4()
		print("%s: Siebel Tools closed.."%time.strftime("%d %b %Y %H:%M:%S",time.localtime()))
	except:
		app.kill()
		print("%s: Siebel Tools closed due to exception."%time.strftime("%d %b %Y %H:%M:%S",time.localtime()))
		raise
def main():
	print("*"*60+"\n\n\tAuto Incremental Compilation for Siebel Tools\n\t\tversion: 1.8\n\n"+"*"*60)

	if len(sys.argv) < 2:
		print("Usage: %s configfile \nexample: %s configfile.ini"%(sys.argv[0],sys.argv[0]))
		sys.exit()
	else:
		configFile = sys.argv[1]
	autoCompile(configFile)

if __name__ == "__main__":
	main()