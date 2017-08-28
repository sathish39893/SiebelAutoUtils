import csv,re,os,sys
#########
def validateInputs(filename):
	if filename != "" and os.path.exists(filename.strip("\"").strip("\'")) is False:
		print('filename: %s does not exists'%filename)
		sys.exit()

def getRepoNonRepoType(ObjType):
	ObjTypeList ={'SRF':['Bitmap Category','Business Component','Business Object','Business Service','Class','Find','HTML Heirarchy Bitmap','Help Id','Icon Map','Integration Object',
						'Application','Applet','Link','Menu','Message Category','Pick List','Project','Screen','Symbolic String','Table','Task Group','Toolbar','View','Web Page',
						'Import Object'],
				'Non-SRF':['List Of Values','Web Service','EAI DataMap','Application DataMap','Workflow','Workflow Policy','SWT Files','JS Files','CSS Files']
				}
	for k in ObjTypeList:
		if k == ObjType:
			return k
		else:
			for v in ObjTypeList[k]:
				if ObjType == v:
					return k
	return None
def getObjType(searchFor):
	#added below to avoid typo errors
	ObjectList = {	'Bitmap Category':["BITMAP CATEGORY","BITMAP"],
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
				'View':['VIEW'],
				'Web Page':['WEB PAGE'],
				'Web Template':['WEB TEMPLATE','WEB TEMPL','WEBTEMPL'],
				'Import Object':['IMPORT OBJECT'],
				# non - repository
				'List Of Values':['LOV''LOVS','DESCRIPTION','VALUE','TYPE'],
				'Web Service':['WS','WEBSERVICE','INBOUND WS','OUTBOUND WS'],
				'EAI DataMap':['DATAMAP','DATA MAP'],
				'Application DataMap':['APPLICATION DATAMAP','APPLICATION DATA MAP'],
				'Workflow':['WF','WORKFLOW'],
				'Workflow Policy':['WF POLICY','WORKFLOW POLICY'],
				'SWT Files':['SWT','SWT FILES'],
				'JS Files':['JS FILES','JAVASCRIPT FILES','JAVA SCRIPT FILES'],
				'CSS Files':['CSS FILES','CSS']
			}
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
			print("Started generating Object List file '%s'."%ObjListFileName)
			headerList = ['Id','Defect Type','Project','Owner','Object Type','Object Name','SRF/Non-SRF','Owning Team']
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
		IdColumn,ObjListColumn,defectType,projectName,ownerName,ownerTeam = "","","","","",""
		ObjListofList = []
		objList = []
		for rownum,row in enumerate(adtreader):
			if rownum == 0: 
				IdColumn = findColumn("Id",row)
				ObjListColumn = findColumn("Resolution ADT",row)
				defectTypeColumn = findColumn("Defect Type",row)
				projectNameColumn = findColumn("Custom 2_ Defect",row)
				ownerNameColumn = findColumn("Owned By",row)
				ownerTeamColumn = findColumn('Custom 3_ Defect',row)
				
				#print(IdColumn,ObjListColumn)
			adtObjList = row[ObjListColumn]
			adtNum = row[IdColumn]
			if defectTypeColumn is not None: defectType = row[defectTypeColumn]
			projectName = row[projectNameColumn]
			if ownerNameColumn is not None: ownerName = row[ownerNameColumn]
			if ownerTeamColumn is not None: ownerTeam = row[ownerTeamColumn]
			
			if adtNum != "" and adtObjList !="":
				objListArr = adtObjList.split("\n")
				for line in objListArr:
					if line !="":
						pattern = "(.*?\s*):(\s*.*?$)"    ## pattern used for matching
						m = re.search(pattern,line)
						if m is not None:
							objTypelist = str(m.group(1).strip()).split(" ")
							objNamelist = str(m.group(2).strip()).split("->")
							objName = objNamelist[0].strip("-")
							for objType in objTypelist:
								newObjType = getObjType(objType)
								objList = []
								if newObjType is not None:
									srfObjType = getRepoNonRepoType(newObjType)
									if newObjType == "Workflow":objName = str(objName.split(":")[0].strip(""))
									objList.append(adtNum)
									objList.append(defectType)
									objList.append(projectName)
									objList.append(ownerName)
									objList.append(newObjType)
									objList.append(objName)
									objList.append(srfObjType)
									objList.append(ownerTeam)
									ObjListofList.append(objList)
			elif adtObjList == "":
				objList = []
				objList.append(adtNum)
				objList.append(defectType)
				objList.append(projectName)
				objList.append(ownerName)
				objList.append("None")#newObjType
				objList.append("None")#objName
				objList.append("None")#srfObjType
				objList.append(ownerTeam)
				ObjListofList.append(objList)
		#print(ObjListofList)
		#for objrow in ObjListofList:
		print("Total number of ADTs scanned:%i"%(rownum))
		createObjListFile(filename,ObjListofList)
def main():
	print("*"*60+"\n\n\tObjects List Generator for ADT list\n\t\tversion: 0.3\n\n"+"*"*60)

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