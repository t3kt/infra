from typing import Optional, Union

from infraHosting import ComponentSpec

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from ..componentLoader.componentLoader import ComponentLoader

	class _Comp(COMP):
		pass

	# noinspection PyTypeHints
	iop.componentLoader = ComponentLoader(COMP())  # type: Union[COMP, ComponentLoader]

try:
	# noinspection PyUnresolvedReferences
	CallbacksExt = op.TDModules.op('TDCallbacksExt').module.CallbacksExt
except ImportError:
	from _stubs.TDCallbacksExt import CallbacksExt

class SceneLoader(CallbacksExt):
	def __init__(self, ownerComp: 'COMP'):
		super().__init__(ownerComp)
		# noinspection PyTypeChecker
		self.ownerComp = ownerComp  # type: _Comp

	@staticmethod
	def _sceneComponent() -> 'Optional[COMP]':
		return iop.componentLoader.Component

	@staticmethod
	def _sceneTox() -> 'Optional[str]':
		return iop.componentLoader.ComponentTox

	def UnloadScene(self):
		iop.componentLoader.UnloadComponent()
		raise NotImplementedError()

	def LoadSceneTox(
			self,
			toxPath: str,
			forceLoad: bool = False,
	):
		if self._needsToChangeTox(toxPath, forceLoad):
			self.UnloadScene()
		raise NotImplementedError()

	def LoadComponentSpec(
			self,
			spec: 'ComponentSpec',
			forceLoad: bool = False,
	):
		if self._needsToChangeTox(spec.tox, forceLoad):
			self.UnloadScene()
		raise NotImplementedError(0)

	def BuildComponentSpec(self) -> Optional['ComponentSpec']:
		raise NotImplementedError()

	def _needsToChangeTox(self, newToxPath: Optional[str], forceLoad: bool = False):
		if forceLoad:
			return True
		currentTox = self._sceneTox()
		if not currentTox:
			return bool(newToxPath)
		if not newToxPath:
			return False
		if newToxPath != currentTox:
			return True
		return False

	def Unloadcsene(self, _=None):
		self.UnloadScene()
