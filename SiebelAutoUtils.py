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
import argparse,configparser
import AutoIncrementCompile,ImportSIF,exportSIF

print("*"*60+"\n\n\tAutomated utilities for Siebel Tools\n\t\tversion: 1.0\n\n"+"*"*60+"\n")
def main():
	argParser = argparse.ArgumentParser()
	argParser.add_argument("-o","--option", required=True, help="Options to be specified: compile,importsif,exportsif")
	argParser.add_argument("-c","--cfgfile",required=True, help="configuration file name")
	args = argParser.parse_args()

	if args.option.lower() == "compile":
		print("Option selected: incremental compile")
		AutoIncrementCompile.autoCompile(args.cfgfile)
	elif args.option.lower() == "importsif":
		print("Option selected: import sif")
		ImportSIF.importSIF(args.cfgfile)
	elif args.option.lower() =="exportsif":
		print("Option selected: export sif")
		exportSIF.exportSIF(args.cfgfile)
	else:
		print("invalid option:please select options compile,importsif,exportsif")

if __name__ == "__main__":
	main()