from typing import Optional

from infraMeta import CompMeta

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from _typeAliases import *

	class _ConfigPar:
		Toolkitroot: OPParamT
		Toolkitmeta: OPParamT
		Categorytags: StrParamT
		Componenttags: StrParamT
	class _ConfigComp(COMP):
		par: _ConfigPar

try:
	# noinspection PyUnresolvedReferences
	CallbacksExt = op.TDModules.op('TDCallbacksExt').module.CallbacksExt
except ImportError:
	from _stubs.TDCallbacksExt import CallbacksExt

class ToolkitTools(CallbacksExt):
	def __init__(self, ownerComp: 'COMP'):
		super().__init__(ownerComp)

	def _toolkitConfig(self) -> 'Optional[_ConfigComp]':
		return self.ownerComp.par.Toolkitconfig.eval()

	def UpdateComponentMetadata(
			self,
			comp: 'COMP',
			incrementVersion=False,
			**kwargs):
		pass

