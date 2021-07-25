from typing import Union

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from ..workspace.workspace import Workspace

	# noinspection PyTypeHints
	iop.workspace = Workspace(COMP())  # type: Union[Workspace, COMP]

try:
	# noinspection PyUnresolvedReferences
	CallbacksExt = op.TDModules.op('TDCallbacksExt').module.CallbacksExt
except ImportError:
	from _stubs.TDCallbacksExt import CallbacksExt

class WorkspaceScenePicker(CallbacksExt):
	pass



