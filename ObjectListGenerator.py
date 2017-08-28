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
				'Non-SRF':['List Of Values','Web Service','Data Map']
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
				'Data Map':['DATAMAP','DATA MAP']
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
		with open(filename+"_ObjectList.csv", 'w',newline='',encoding="utf-16") as ObjListFile:
			print("Started generating Object List file '%s'."%filename)
			headerList = ['Id','Defect Type','Project','Owner','Object Type','Object Name','SRF/Non-SRF']
			ObjListWriter = csv.writer(ObjListFile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_ALL) #QUOTE_MINIMAL
			ObjListWriter.writerow(headerList)
			for row in rowTowrite:
				ObjListWriter.writerow(row)
		print("Object List file '%s' generated."%filename)
	except:
		print("failed to generate Object List file '%s'."%filename)
		raise
	
def parseObjList(filename):
	
	with open(filename,encoding="utf-16") as csvfile:
		adtreader = csv.reader(csvfile,dialect="excel",delimiter='\t',quotechar='"')
		IdColumn,ObjListColumn,defectType,projectName,ownerName = "","","","",""
		ObjListofList = []
		Objlist = []
		for rownum,row in enumerate(adtreader):
			if rownum == 0: 
				IdColumn = findColumn("Id",row)
				ObjListColumn = findColumn("Resolution ADT",row)
				defectTypeColumn = findColumn("Defect Type",row)
				projectNameColumn = findColumn("Custom 2_ Defect",row)
				ownerNameColumn = findColumn("Owned By",row)
				
				#print(IdColumn,ObjListColumn)
			objList = row[ObjListColumn]
			adtNum = row[IdColumn]
			defectType = row[defectTypeColumn]
			projectName = row[projectNameColumn]
			ownerName = row[ownerNameColumn]
			if adtNum != "" and objList !="":
				objListArr = objList.split("\n")
				for line in objListArr:
					if line !="":
						pattern = "(.*?\s*):(\s*.*?$)"    ## pattern used for matching
						m = re.search(pattern,line)
						if m is not None:
							objTypelist = str(m.group(1).strip()).split(" ")
							objName = str(m.group(2).strip())
							for objType in objTypelist:
								newObjType = getObjType(objType)
								if newObjType is not None:
									Objlist = []
									srfObjType = getRepoNonRepoType(newObjType)
									Objlist.append(adtNum)
									Objlist.append(defectType)
									Objlist.append(projectName)
									Objlist.append(ownerName)
									Objlist.append(newObjType)
									Objlist.append(objName)
									Objlist.append(srfObjType)
									ObjListofList.append(Objlist)
		#print(ObjListofList)
		#for objrow in ObjListofList:
		createObjListFile(filename,ObjListofList)
def main():
	print("*"*60+"\n\n\tObjects List Generator for ADT list\n\t\tversion: 0.2\n\n"+"*"*60)

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