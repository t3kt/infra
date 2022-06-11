# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from .libraryTools import LibraryTools

def onUpdateComponentMetadata(info: dict):
	libraryTools = info['libraryTools']  # type: LibraryTools
	comp = info['comp']  # type: COMP
	params = info.get('params') or {}  # type: dict
	pass

def onSaveComponent(info: dict):
	libraryTools = info['libraryTools']  # type: LibraryTools
	comp = info['comp']  # type: COMP
	params = info.get('params') or {}  # type: dict
	pass

def onUpdatePackageMetadata(info: dict):
	libraryTools = info['libraryTools']  # type: LibraryTools
	comp = info['comp']  # type: COMP
	params = info.get('params') or {}  # type: dict
	pass

def onSavePackage(info: dict):
	libraryTools = info['libraryTools']  # type: LibraryTools
	comp = info['comp']  # type: COMP
	params = info.get('params') or {}  # type: dict
	pass

