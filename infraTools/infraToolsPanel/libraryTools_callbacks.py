# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from .libraryTools import LibraryTools
	from infraMeta import CompInfo

def onUpdateComponentMetadata(info: dict):
	libraryTools = info['libraryTools']  # type: LibraryTools
	comp = info['comp']  # type: COMP
	params = info.get('params') or {}  # type: dict
	compInfo = info.get('compInfo')  # type: CompInfo
	pass

def onSaveComponent(info: dict):
	libraryTools = info['libraryTools']  # type: LibraryTools
	comp = info['comp']  # type: COMP
	params = info.get('params') or {}  # type: dict
	compInfo = info.get('compInfo')  # type: CompInfo
	pass
