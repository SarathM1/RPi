import logging
import sys

def debugLog(fName):
	
	lgr = logging.getLogger(fName)
	lgr.setLevel(logging.DEBUG)
	

	fh = logging.FileHandler(fName+'.log')
	
	fh.setLevel(logging.DEBUG)

	
	frmt = logging.Formatter('%(asctime)s \t %(message)s\n',"%Y-%m-%d %H:%M:%S")
	fh.setFormatter(frmt)
	
	lgr.addHandler(fh)
	return lgr

def liveLog(fName):
	lgr = logging.getLogger(fName)
	lgr.setLevel(logging.DEBUG)
	

	fh = logging.FileHandler(fName+'.log')
	
	fh.setLevel(logging.DEBUG)

	
	frmt = logging.Formatter('%(asctime)s \t %(message)s\n',"%Y-%m-%d %H:%M:%S")
	fh.setFormatter(frmt)
	
	lgr.addHandler(fh)
	return lgr

def backfillLog(fName):
	lgr = logging.getLogger(fName)
	lgr.setLevel(logging.DEBUG)
	

	fh = logging.FileHandler(fName+'.log')
	
	fh.setLevel(logging.DEBUG)

	
	frmt = logging.Formatter('%(asctime)s \t %(message)s\n',"%Y-%m-%d %H:%M:%S")
	fh.setFormatter(frmt)
	
	lgr.addHandler(fh)
	return lgr

