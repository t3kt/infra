# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from .libraryPalette import LibraryPalette

	ext.palette = LibraryPalette(COMP())


def onPickItem(info: dict):
	item = info['item']
	ext.palette.picker_onPickItem(item)

def onEditItem(info: dict):
	item = info['item']
	pass

def onListRefresh(info: dict):
	picker = info['picker']
	listComp = info['listComp']
	rowHeight = info['rowHeight']
	ext.palette.picker_onListRefresh(listComp, rowHeight)
