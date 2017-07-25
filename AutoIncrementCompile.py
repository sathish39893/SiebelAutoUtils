'''
Auto Incremental Compilation for Siebel Tools

Author: SATHISH PANTHAGANI
Inputs:

Outputs:

'''

from pywinauto.application import Application
import os,sys,time

ToolsWinTitle = 'Siebel Tools - Siebel Repository'
ToolsexePath = r"C:\Siebel\15.0.0.0.0\Tools\BIN\siebdev.exe"
cfgPath = r'c:\Siebel\15.0.0.0.0\Tools\bin\enu\tools.cfg'
userName = "SPANTH"
passWord = "SPANTH"
dataSource = "Local"
ToolsPath = ToolsexePath+" /c "+cfgPath+" /u "+userName+" /p "+passWord+" /d "+dataSource
srfFile = r"C:\Siebel\15.0.0.0.0\Client\OBJECTS\enu\siebel_sia_auto.srf"
#print(ToolsPath)

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
	print("validation successful")

validateInputs()
#Launch Tools
#app = Application().start(ToolsPath,timeout=100)
app = Application().connect(path=ToolsexePath)

app[ToolsWinTitle].wait("exists enabled visible ready")
dlg = app.top_window() #dlg = app['Siebel Tools - Siebel Repository']
dlg.type_keys("^E") # to open Object Explorer
objexpl = app.SiebelToolsSiebelRepository.ObjectExplorer1.TreeView.WrapperObject() #Object explorer window

#Query for the compile Objects --Applet
#targetobj = objexpl.get_item(r'\Siebel Objects\Application').click() #click on object explorer items
#dlg.type_keys("^Q") #Working
#app[ToolsWinTitle]['~ApplicationsEdit'].set_edit_text("ABO Bulk Request Screen")
#dlg.type_keys("^{ENTER}")

def compileObj():
	app[ToolsWinTitle].type_keys("^{F7}") #Opens Compilation Window
	app['Object Compiler']['Siebel repository file:Edit'].set_edit_text(srfFile) #SRF File location
	app['Object Compiler']['Compile'].click()  #Compilation Starts
	errMsg = ""
	#if(app.top_window().title == app['Error'].title):
	#if(app['Error']):
	#	errMsg = app['Error']['ErrorEdit'].TextBlock()
	#	app['Error']['OK'].click()
	#	if(errMsg):
	#		print(errMsg)
	app['Object Compiler']['Compile'].wait_not('visible')

#Query for the compile Objects -- Application
def QuerynCompileObjects(ObjType, ObjName):
	sEditCtrl = "~"+ObjType+"sEdit" #Object Plural Form is used for this window
	sTreeObjPath = '\\Siebel Objects\\'+ObjType
	#print("Edit Control: "+sEditCtrl)
	#print("sTreeObjPath: "+sTreeObjPath)
	targetobj = objexpl.get_item(sTreeObjPath).click() #click on object explorer items
	
	app[ToolsWinTitle][sEditCtrl].wait('visible') # It will wait till the window appears
	
	dlg.type_keys("^Q") # Query for the object Name
	app[ToolsWinTitle][sEditCtrl].set_edit_text(ObjName)
	dlg.type_keys("^{ENTER}")
	compileObj() # Compiles Object
	

print("Compilation Started...")
QuerynCompileObjects("Application","ABO Bulk Request Screen")
QuerynCompileObjects("Integration Object","ABO Bulk Request")
QuerynCompileObjects("Business Component","ABO Bulk Request - Orders")
QuerynCompileObjects("Business Object","ABO Bulk Request")
QuerynCompileObjects("Business Service","ABO Bulk Request Import Service")
QuerynCompileObjects("Command","AccountMatch")
QuerynCompileObjects("Pick List","ABO Bulk Request Action Field Picklist")
QuerynCompileObjects("Screen","Accounts Screen")
QuerynCompileObjects("View","A Account Partner View")
print("Compilation End...")
# Close/exit Siebel Tools

#dlg.close_alt_f4()

