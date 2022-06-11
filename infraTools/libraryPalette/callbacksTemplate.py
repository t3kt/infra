# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

def onCreateComp(info: dict):
	newOp = info['newOp']
	template = info['template']
	item = info['item']
	palette = info['palette']

def onError(info: dict):
	message = info['message']
	palette = info['palette']

def onMessage(info: dict):
	message = info['message']
	palette = info['palette']
