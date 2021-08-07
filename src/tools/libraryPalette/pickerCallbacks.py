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
