'''
Auto Incremental Compilation for Siebel Tools

Author: SATHISH PANTHAGANI
email: sathish.panthagani@accenture.com
Inputs: Tools Path, SRF File Path, Object List File

Outputs: Compilation Objects to SRF File

'''

import argparse,configparser
import AutoIncrementCompile
import importSIF
import exportSIF

print("*"*60+"\n\n\tAutomated utilities for Siebel Tools\n\t\tversion: 1.0\n\n"+"*"*60+"\n")
def main():
	argParser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
	description="This utility does the following jobs:\n\r1. export sif files from source environment\n\r2. import sif files to target environment\n\r3. automatic incremental compile")
	
	argParser.add_argument("-o","--option", required=True, choices=["exportsif","importsif","compile"],help="mode of this tool to run")
	argParser.add_argument("-c","--cfgfile",required=True, help="name of the configuration file")
	args = argParser.parse_args()

	if args.option.lower() == "compile":
		print("Selected option: incremental compile")
		AutoIncrementCompile.autoCompile(args.cfgfile)
	elif args.option.lower() == "importsif":
		print("Selected option: import sif")
		importSIF.importSIF(args.cfgfile)
	elif args.option.lower() =="exportsif":
		print("Selected option: export sif")
		exportSIF.exportSIF(args.cfgfile)
	else:
		print("invalid option:use following options: compile importsif exportsif")

if __name__ == "__main__":
	main()