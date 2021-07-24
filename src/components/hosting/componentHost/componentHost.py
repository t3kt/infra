from typing import Optional

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from _typeAliases import *

	class _Pars:
		Hostcontainer: OPParamT
	class _COMP(COMP):
		par = _Pars()

	class _StatePars:
		Hostedcomp: OPParamT
	class _StateComp(COMP):
		par = _StatePars()

	ipar.hostState = _StatePars()

class ComponentHost:
	def __init__(self, ownerComp: 'COMP'):
		# noinspection PyTypeChecker
		self.ownerComp = ownerComp  # type: _COMP

	def _getHostedComponent(self) -> 'Optional[COMP]':
		comp = ipar.hostState.Hostedcomp.eval()
		if comp and comp.valid:
			return comp

		pass
