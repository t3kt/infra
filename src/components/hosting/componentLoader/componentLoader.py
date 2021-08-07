from pathlib import Path
from typing import List, Optional, Type, Union

from infraHosting import ComponentSpec

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from _typeAliases import *

	class _LoaderPar:
		Hostmode: StrParamT
		Toxtoload: StrParamT

	class _LoaderComp(COMP):
		par: _LoaderPar

try:
	# noinspection PyUnresolvedReferences
	CallbacksExt = op.TDModules.op('TDCallbacksExt').module.CallbacksExt
except ImportError:
	from _stubs.TDCallbacksExt import CallbacksExt

class ComponentLoader(CallbacksExt):
	def __init__(self, ownerComp: 'COMP'):
		super().__init__(ownerComp)
		# noinspection PyTypeChecker
		self.ownerComp = ownerComp  # type: _LoaderComp

	@property
	def _useEngine(self):
		return self.ownerComp.par.Hostmode == 'engine'

	@property
	def Component(self) -> 'Optional[COMP]':
		if self._useEngine:
			return self._engine if self._engine.par.file else None
		return self._localComponent

	@property
	def _localComponent(self) -> 'Optional[COMP]':
		for o in self.ownerComp.children:
			if not o.isCOMP:
				continue
			if isinstance(o, engineCOMP) or o.name == 'componentMeta':
				continue
			# noinspection PyTypeChecker
			return o

	@property
	def IsLoaded(self):
		if self._useEngine:
			engine = self._engine
			return bool(engine.par.file and not engine.warnings())
		else:
			return bool(self._localComponent)

	@property
	def IsLoading(self):
		if self._useEngine:
			return bool(self._engine.par.file) and bool(self._engine.warnings())
		return False

	@property
	def LoadingStatus(self):
		if self.IsLoading:
			return 'loading'
		if self.IsLoaded:
			return 'loaded'
		return 'unloaded'

	@property
	def _engine(self) -> 'engineCOMP':
		return self.ownerComp.op('engine')

	@property
	def ComponentTox(self) -> 'Optional[str]':
		if self._useEngine:
			return self._engine.par.file.eval()
		comp = self._localComponent
		return comp and comp.par.externaltox.eval()

	@property
	def ComponentName(self) -> 'Optional[str]':
		if self._useEngine:
			tox = self.ComponentTox
			if tox:
				return Path(tox).stem
		comp = self._localComponent
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
		elif self._useEngine:
			reused = True  # TODO: is this correct?
			comp = self._engine
			comp.par.file = spec.tox
			comp.par.initialize.pulse()
		else:
			reused = False
			comp = spec.createComp(self.ownerComp, resetDefault=resetDefault, includeParams=includeParams)
		self.ownerComp.par.Toxtoload = spec.tox or ''
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
		if self._useEngine:
			comp = self._engine
			comp.par.file.val = ''
			comp.par.unload.pulse()
		else:
			comp = self.Component
			if not comp:
				return
			# noinspection PyBroadException
			try:
				comp.destroy()
			except:
				pass
		# self.ownerComp.par.Toxtoload = ''
		run('args[0]()', self._cleanUpUnload)
		self.DoCallback('onComponentUnloaded')

	def _cleanUpUnload(self):
		dat = self.ownerComp.op('extensionParExec')
		dat.clearScriptErrors()

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

	def Loadcomponent(self, _=None):
		self.LoadComponent(tox=self.ownerComp.par.Toxtoload.eval())

	def findVideoOutput(self):
		return self._findOutput(
			TOP,
			'video_out', 'image_out', 'out1', 'out2')

	def findAudioOutput(self):
		return self._findOutput(
			CHOP,
			'audio_out', 'sound_out', 'out1', 'out2')

	def findTableOutput(self):
		return self._findOutput(
			DAT,
			'table_out', 'mappings_out', 'out1', 'out2', 'out3')

	def _findOutput(self, opType: Type[OP], *names: str):
		comp = self.Component
		if not comp:
			return None
		outs = [conn.outOP for conn in comp.outputConnectors if isinstance(conn.outOP, opType)]
		byName = {o.name: o for o in outs}
		for name in names:
			if name in byName:
				return byName[name]
		for out in outs:
			return out

