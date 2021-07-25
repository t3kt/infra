from pathlib import Path
from typing import List, Optional, Type, Union

from infraHosting import ComponentSpec

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

try:
	# noinspection PyUnresolvedReferences
	CallbacksExt = op.TDModules.op('TDCallbacksExt').module.CallbacksExt
except ImportError:
	from _stubs.TDCallbacksExt import CallbacksExt

class ComponentLoader(CallbacksExt):
	def __init__(self, ownerComp: 'COMP'):
		super().__init__(ownerComp)

	@property
	def Component(self) -> 'Optional[COMP]':
		for o in self.ownerComp.children:
			if o.isCOMP:
				return o

	@property
	def ComponentTox(self) -> 'Optional[str]':
		comp = self.Component
		return comp and comp.par.externaltox.eval()

	@property
	def ComponentName(self) -> 'Optional[str]':
		comp = self.Component
		return comp and comp.name

	def LoadComponent(self, tox: 'Union[str, Path]', name: str = None) -> 'COMP':
		convertedPath = Path(tox).as_posix()
		spec = ComponentSpec(
			name=name,
			tox=convertedPath,
		)
		return self.LoadComponentSpec(
			spec,
			forceLoad=True,
		)

	def LoadComponentSpec(
			self,
			spec: 'ComponentSpec',
			forceLoad: bool = False,
			resetDefault=False,
			includeParams: List[Par] = None,
	):
		comp = self.Component
		if self._needsToChangeTox(spec.tox, forceLoad):
			if comp:
				self.UnloadComponent()
		if comp:
			reused = True
			spec.applyParams(comp, resetDefault=resetDefault, includeParams=includeParams)
		else:
			reused = False
			comp = spec.createComp(self.ownerComp, resetDefault=resetDefault, includeParams=includeParams)
		self.DoCallback('onComponentLoaded', {
			'comp': comp,
			'tox': Path(spec.tox).as_posix(),
			'reused': reused,
			'spec': spec,
			'forceLoad': forceLoad,
		})
		return comp

	def GetComponentSpec(
			self,
			includeParams: List[Par] = None,
			excludeReadOnly=False,
	) -> Optional['ComponentSpec']:
		comp = self.Component
		if not comp:
			return None
		return ComponentSpec.extractFromOp(
			comp, includeParams=includeParams, excludeReadOnly=excludeReadOnly)

	def _needsToChangeTox(self, newToxPath: Optional[str], forceLoad: bool = False):
		if forceLoad:
			return True
		currentTox = self.ComponentTox
		if not currentTox:
			return True
		if newToxPath != currentTox:
			return True
		return False

	def CreateNewComponent(
			self, tox: 'Union[str, Path]', name: str = None,
			template: 'Optional[COMP]' = None,
			compType: 'Optional[Type[COMP]]' = None,
			autoSave=True) -> 'COMP':
		self.UnloadComponent()
		if not name:
			path = Path(tox)
			name = path.stem
		if template:
			comp = self.ownerComp.copy(template, name=name, includeDocked=False)
		else:
			comp = self.ownerComp.create(compType or baseCOMP, name)
		comp.name = name
		convertedPath = Path(tox).as_posix()
		comp.par.externaltox = convertedPath
		if autoSave:
			comp.save(convertedPath, createFolders=True)
		self.DoCallback('onComponentCreated', {
			'comp': comp,
			'tox': convertedPath,
		})
		return comp

	def UnloadComponent(self):
		comp = self.Component
		if not comp:
			return
		# noinspection PyBroadException
		try:
			comp.destroy()
		except:
			pass
		self.DoCallback('onComponentUnloaded')

	def SaveComponent(self, tox: 'Optional[Union[str, Path]]' = None):
		comp = self.Component
		if not comp:
			return
		if tox:
			tox = Path(tox)
			comp.par.externaltox = tox.as_posix()
		else:
			tox = Path(self.ComponentTox)
		comp.save(tox.as_posix(), createFolders=True)
		self.DoCallback('onComponentSaved', {
			'comp': comp,
			'tox': tox.as_posix(),
		})

	def SaveComponentSpec(
			self,
			specPath: Union[str, Path],
			includeParams: List[Par] = None,
			excludeReadOnly=False,
	):
		spec = self.GetComponentSpec(includeParams, excludeReadOnly)
		if not spec:
			return
		path = Path(specPath)
		path.parent.mkdir(parents=True)
		spec.saveSpecFile(path)
		self.DoCallback('onComponentSpecSaved', {
			'comp': self.Component,
			'spec': spec,
			'specPath': specPath.as_posix(),
		})

	def Savecomponent(self, _=None):
		self.SaveComponent()

	def Unloadcomponent(self, _=None):
		self.UnloadComponent()
