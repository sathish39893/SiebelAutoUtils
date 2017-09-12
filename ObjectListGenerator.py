'''
	Object list generator for ADT tool (version 0.4)
	Author: Sathish.panthagani@accenture.com
	
	this tool uses the adt tool query export csv file and parses 
	the Resolution ADT column details to make a object list file in CSV format.
	This will help to created object list in automated way.
	

'''

import csv,re,os,sys

def validateInputs(filename):
	if filename != "" and os.path.exists(filename.strip("\"").strip("\'")) is False:
		print('filename: %s does not exists'%filename)
		sys.exit()

def getRepoNonRepoType(ObjType):
	ObjTypeList ={'SRF':['Bitmap Category','Business Component','Business Object','Business Service','Class','Find','HTML Heirarchy Bitmap','Help Id','Icon Map','Integration Object',
						'Application','Applet','Link','Menu','Message Category','Pick List','Project','Screen','Symbolic String','Table','Task Group','Toolbar','View','Web Page',
						'Import Object'],
				'Non-SRF':['List Of Values','Web Service','EAI DataMap','Application DataMap','Workflow','Workflow Policy','Workflow Policy Action','SWT Files','JS Files','CSS Files',
						'Attribute Definition','Product Definition','PDQ','RCR','Images']
				}
	for k in ObjTypeList:
		if k == ObjType:
			return k
		else:
			for v in ObjTypeList[k]:
				if ObjType == v:
					return k
	return None

def getModifiedInfo(objUpdInfo):
	ObjTypeList ={'Modified':['UPD','UPDATED','UPDATE','EDIT','MODIFIED'],
				'New':['ADD','ADDED','NEW','CREATE','CREATED']
				}
	for k in ObjTypeList:
		if k == objUpdInfo:
			return k
		else:
			for v in ObjTypeList[k]:
				if objUpdInfo.upper() == v:
					return k
	return None

def getObjType(searchFor):
	#added below to avoid typo errors
	ObjectList = {	'Bitmap Category':['BITMAP CATEGORY','BITMAP','BITMAPCATEGORY'],
				'Business Component':['BUSINESS COMPONENT','BC', 'BUSCOMP'],
				'Business Object':['BUSINESS OBJECT','BO'], 
				'Business Service':['BUSINESS SERVICE','BS'],
				'Class':['CLASS'],
				'Command':['COMMAND'],
				'Find':['FIND'],
				'HTML Heirarchy Bitmap':['HTML HEIRARCHY BITMAP','HTMLHEIRARCHYBITMAP'],
				'Help Id':['HELP ID'],
				'Icon Map':['ICON MAP','ICON'],
				'Integration Object':['INTEGRATION OBJECT','IO','INT OBJ'],
				'Application':['APPLICATION','APP','APPL'],
				'Applet':['APPLET'],  #application and applet needs to be same sequence
				'Link':['LINK'],
				'Menu':['MENU'],
				'Message Category':['MESSAGE CATEGORY','MESSAGECATEGORY'],
				'Pick List':['PICK LIST','PICKLIST'],
				'Project':['PROJECT'],
				'Screen':['SCREEN'],
				'Symbolic String':['SYMBOLIC STRING','SYMBOLICSTRINGS','SYMBOLICSTRING'],
				'Table':['TABLE'],
				'Task Group':['TASK GROUP','TASKGROUP'],
				'Toolbar':['TOOLBAR'],
				'View':['VIEW'],
				'Web Page':['WEB PAGE'],
				'Web Template':['WEB TEMPLATE','WEB TEMPL','WEBTEMPL'],
				'Import Object':['IMPORT OBJECT','IMPORTOBJECT'],
				# non - repository
				'List Of Values':['LOV','LOVS','DESCRIPTION','VALUE','TYPE','LIST OF VALUES'],
				'Web Service':['WS','WEBSERVICE','INBOUND WS','OUTBOUND WS','INBOUNDWS','OUTBOUNDWS'],
				'EAI DataMap':['DATAMAP','DATA MAP','DM'],
				'Application DataMap':['APPLICATION DATAMAP','APPLICATION DATA MAP','APPLICATIONDATAMAP'],
				'Workflow':['WF','WORKFLOW'],
				'Workflow Policy':['WF POLICY','WORKFLOW POLICY','WORKFLOWPOLICY'],
				'Workflow Policy Action':['WFPOLICYACTION','WORKFLOW POLICY ACTION','WORKFLOWPOLICYACTION','WORKFLOWPOLICYACTIONS'],
				'SWT Files':['SWT','SWT FILES','SWTFILES'],
				'JS Files':['JS FILES','JSFILES','JAVASCRIPT FILES','JAVA SCRIPT FILES','JAVASCRIPTFILES','JAVASCRIPTFILE'],
				'CSS Files':['CSS FILES','CSS'],
				'Attribute Definition':['ATTRIBUTE DEFINITION','ATTRIBUTE'],
				'Product Definition':['PRODUCT DEFINITION','PRODUCT'],
				'PDQ':['PDQ','PREDEFINEDQUERIES','PRE DEFINED QUERIES'],
				'RCR':['RCR','REPEATING COMPONENT REQUESTS','REPEATING COMPONENT REQUEST','REPEATINGCOMPONENTREQUEST','REPEATINGCOMPONENTREQUESTS'],
				'Images':['IMAGE','IMAGES']
			}
	searchFor = re.sub(r'[^a-zA-Z]','',searchFor)
	for k in ObjectList:
		if k == searchFor:
			return k
		else:
			for v in ObjectList[k]:
				if searchFor.upper() == v:
					return k
	return None
	
def findColumn(element,findToList):
	try:
		return findToList.index(element)
	except ValueError:
		return None
		
def createObjListFile(filename,rowTowrite):
	try:
		ObjListFileName = str(filename+"_ObjectList.csv")
		with open(ObjListFileName, 'w',newline='',encoding="utf-16") as ObjListFile:
			headerList = ['Id','Defect Type','Project','Owner','Object Type','Object Name','SRF/Non-SRF','SIT','UAT','New/Modified','Owning Team']
			ObjListWriter = csv.writer(ObjListFile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_ALL) #QUOTE_MINIMAL
			ObjListWriter.writerow(headerList)
			for row in rowTowrite:
				ObjListWriter.writerow(row)
		print("Object List file '%s' generated."%ObjListFileName)
	except:
		print("failed to generate Object List file '%s'."%ObjListFileName)
		raise
	
def parseObjList(filename):
	
	with open(filename,encoding="utf-16") as csvfile:
		adtreader = csv.reader(csvfile,dialect="excel",delimiter='\t',quotechar='"')
		IdColumn,ObjListColumn,defectType,projectName,ownerName,ownerTeam,objName,objUpdInfo = "","","","","","","",""
		ObjListofList = []
		objList = []
		for rownum,row in enumerate(adtreader):
			matchFound = "false"
			
			if rownum == 0: 
				IdColumn = findColumn("Id",row)
				ObjListColumn = findColumn("Resolution ADT",row)
				defectTypeColumn = findColumn("Defect Type",row)
				projectNameColumn = findColumn("Custom 2_ Defect",row)
				ownerNameColumn = findColumn("Owned By",row)
				ownerTeamColumn = findColumn('Custom 3_ Defect',row)
				
				#print(IdColumn,ObjListColumn)
			adtObjList = row[ObjListColumn].strip()
			adtNum = row[IdColumn].strip()
			if defectTypeColumn is not None: defectType = row[defectTypeColumn]
			projectName = row[projectNameColumn]
			if ownerNameColumn is not None: ownerName = row[ownerNameColumn]
			if ownerTeamColumn is not None: ownerTeam = row[ownerTeamColumn]
			
			if adtNum != "" and adtObjList !="" and rownum > 0:
				objListArr = adtObjList.split("\n")
				for line in objListArr:
					if line !="":
						pattern = "(.*?\s*):(\s*.*?$)"    ## pattern used for matching
						m = re.search(pattern,line)
						if m is not None:
							objTypelist = str(m.group(1).strip())
							objTypelist = re.sub(r'[^a-zA-Z]','',objTypelist)
							objTypelist = objTypelist.split(" ")
							objNamelist = str(m.group(2).strip()).split("->")
							objName = objNamelist[0].strip().strip("-").strip() #Object Name
							if len(objNamelist) > 1: objUpdInfo = objNamelist[1].strip("-").strip()
							counter = 0
							lenOfObjType = len(objTypelist)
							skipRow = "false"
							for counter, objType in enumerate(objTypelist):
								if skipRow == "true": break
								if objType.strip() == "": continue
								newObjType = getObjType(objType.strip())
								if newObjType is None and counter < lenOfObjType-1:  # add next word and check
									objType = objTypelist[counter]+objTypelist[counter+1]
									newObjType = getObjType(objType.strip())
								if newObjType is None and counter < lenOfObjType-2: # add next word and check
									objType = objTypelist[counter]+objTypelist[counter+1]+objTypelist[counter+2]
									newObjType = getObjType(objType.strip())
								
								objList = []
								if newObjType is not None and objName !="":
									matchFound = "true"
									skipRow = "true"
									#print(matchFound,counter,objType,newObjType)
									srfObjType = getRepoNonRepoType(newObjType)
									newobjUpdInfo = getModifiedInfo(objUpdInfo)
									sitVer,uatVer = "",""
									if newObjType == "Workflow":
										objName = str(objName.split(":")[0].strip())
										pattern1 = "\((.*?)([0-9?]{1,2})\).*?"    #pattern1 = "(.*?)\((.*?)\).*?\((.*?)\).*"
										findList = re.findall(pattern1,objName)
										for m1 in findList:
											if m1 is not None:
												if str(m1[0]).upper().startswith("SIT"): sitVer = str(m1[1]).strip()
												if str(m1[0]).upper().startswith("UAT"): uatVer = str(m1[1]).strip()
										objName = re.sub(pattern1,'',objName)  # remove versions wf name
										#print(sitVer,uatVer)
									objList.append(adtNum)
									objList.append(defectType)
									objList.append(projectName)
									objList.append(ownerName)
									objList.append(newObjType)
									objList.append(objName)
									objList.append(srfObjType)
									objList.append(sitVer)
									objList.append(uatVer)
									objList.append(newobjUpdInfo)
									objList.append(ownerTeam)
									ObjListofList.append(objList)

									
				if matchFound=="false" and rownum > 0:
					objList = []
					objList.append(adtNum)
					objList.append(defectType)
					objList.append(projectName)
					objList.append(ownerName)
					objList.append("NoMatch")#newObjType
					objList.append("NoMatch") #objName
					objList.append("") #srfObjType
					objList.append("") #sitVer
					objList.append("") #uatVer
					objList.append("") #newobjUpdInfo
					objList.append(ownerTeam)
					ObjListofList.append(objList)

			elif adtObjList == "" and rownum > 0:
				objList = []
				objList.append(adtNum)
				objList.append(defectType)
				objList.append(projectName)
				objList.append(ownerName)
				objList.append("NoDetails")#newObjType
				objList.append("NoDetails") #objName
				objList.append("") #srfObjType
				objList.append("") #sitVer
				objList.append("") #uatVer
				objList.append("") #newobjUpdInfo
				objList.append(ownerTeam)
				ObjListofList.append(objList)

		print("Total number of ADTs scanned:%i"%(rownum))
		createObjListFile(filename,ObjListofList)
def main():
	print("*"*60+"\n\n\tObjects List Generator for ADT list\n\t\tversion: 1.0\n\n"+"*"*60)

	if len(sys.argv) < 2:
		print("Usage: %s adtlistfile.csv \nexample: %s adtlistfile.csv"%(sys.argv[0],sys.argv[0]))
		sys.exit()
	else:
		adtlistfile = sys.argv[1]
	validateInputs(adtlistfile)
	parseObjList(adtlistfile)
	#print(searchObjType("webservice"))
if __name__ == "__main__":
	main()