import csv,re,os,sys
#########
def validateInputs(filename):
	if filename != "" and os.path.exists(filename.strip("\"").strip("\'")) is False:
		print('filename: %s does not exists'%filename)
		sys.exit()

def searchObjType(searchFor):
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
				'Type':['TYPE'],
				'View':['VIEW'],
				'Web Page':['WEB PAGE'],
				'Web Template':['WEB TEMPLATE','WEB TEMPL','WEBTEMPL'],
				'Import Object':['IMPORT OBJECT'],
				# non - repository
				'List Of Values':['LOV''LOVS','DESCRIPTION','VALUE'],
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
	with open(filename+"_ObjectList.csv", 'w',newline='',encoding="utf-16") as ObjListFile:
		ObjListWriter = csv.writer(ObjListFile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_ALL) #QUOTE_MINIMAL
		for row in rowTowrite:
			ObjListWriter.writerow(row)
	print("Object List file '%s' generated."%filename)
	#with open('eggs.csv', 'w+') as csvfile:
	#	spamwriter = csv.writer(csvfile, delimiter=' ',quotechar='|', quoting=csv.QUOTE_MINIMAL)
	#	spamwriter.writerow(['Spam'] * 5 + ['Baked Beans'])
	#	spamwriter.writerow(['Spam', 'Lovely Spam', 'Wonderful Spam'])
	
def parseObjList(filename):
	
	with open(filename,encoding="utf-16") as csvfile:
		adtreader = csv.reader(csvfile,dialect="excel",delimiter='\t',quotechar='"')
		IdColumn,ObjListColumn = "",""
		rownum =0
		ObjListofList = []
		Objlist = []
		for row in adtreader:
			if rownum == 0: 
				IdColumn = findColumn("Id",row)
				ObjListColumn = findColumn("Resolution ADT",row)
				#print(IdColumn,ObjListColumn)
			rownum +=1
			objList = row[ObjListColumn]
			adtNum = row[IdColumn]
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
								newObjType = searchObjType(objType)
								if newObjType is not None:
									Objlist = []
									Objlist.append(adtNum)
									Objlist.append(newObjType)
									Objlist.append(objName)							
			ObjListofList.append(Objlist)
		#print(ObjListofList)
		#for objrow in ObjListofList:
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