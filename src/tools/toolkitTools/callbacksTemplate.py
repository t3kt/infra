# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from .toolkitTools import ToolkitTools
	from infraMeta import CompMeta

def onUpdateComponentMetadata(info: dict):
	toolkitTools = info['toolkitTools']  # type: ToolkitTools
	comp = info['comp']  # type: COMP
	params = info.get('params') or {}  # type: dict
	compMeta = info.get('compMeta')  # type: CompMeta
	pass
