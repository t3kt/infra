# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from .libraryOpPicker import LibraryOpPicker
	ext.picker = LibraryOpPicker(COMP())


# called when Reset parameter is pulsed, or on load

def onInitCell(comp, row, col, attribs):
	if hasattr(ext, 'picker') and hasattr(ext.picker, 'list_onInitCell'):
		ext.picker.list_onInitCell(row, col, attribs)
def onInitRow(comp, row, attribs):
	if hasattr(ext, 'picker') and hasattr(ext.picker, 'list_onInitRow'):
		ext.picker.list_onInitRow(row, attribs)
def onInitCol(comp, col, attribs):
	if hasattr(ext, 'picker') and hasattr(ext.picker, 'list_onInitCol'):
		ext.picker.list_onInitCol(col, attribs)
def onInitTable(comp, attribs):
	if hasattr(ext, 'picker') and hasattr(ext.picker, 'list_onInitTable'):
		ext.picker.list_onInitTable(attribs)

# called during specific events
#
# coords - a named tuple containing the following members:
#   x
#   y
#   u
#   v

def onRollover(comp, row, col, coords, prevRow, prevCol, prevCoords):
	return

def onSelect(comp, startRow, startCol, startCoords, endRow, endCol, endCoords, start, end):
	ext.picker.list_onSelect(endRow=endRow, endCol=endCol, end=end)

def onRadio(comp, row, col, prevRow, prevCol):
	return

def onFocus(comp, row, col, prevRow, prevCol):
	return

def onEdit(comp, row, col, val):
	return

# return True if interested in this drop event, False otherwise
def onHoverGetAccept(comp, row, col, coords, prevRow, prevCol, prevCoords, dragItems):
	return False
def onDropGetAccept(comp, row, col, coords, prevRow, prevCol, prevCoords, dragItems):
	return False

