# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *


def onPickItem(info: dict):
	item = info['item']
	picker = info['picker']
	pass

def onEditItem(info: dict):
	item = info['item']
	picker = info['picker']
	pass

def onListRefresh(info: dict):
	picker = info['picker']
	listComp = info['listComp']
	rowHeight = info['rowHeight']
