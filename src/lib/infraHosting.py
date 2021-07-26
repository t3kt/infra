from dataclasses import asdict, dataclass, field
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from infraCommon import cleanDict

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

logger = logging.getLogger(__name__)

ValueOrExpr = Union[Any, Dict[str, str]]
_ParsT = Optional[Dict[str, ValueOrExpr]]

@dataclass
class ComponentSpec:
	name: Optional[str] = None
	label: Optional[str] = None
	tox: Optional[str] = None
	copyOf: Optional[ValueOrExpr] = None
	pars: _ParsT = field(default_factory=dict)
	master: Optional['COMP'] = None

	@classmethod
	def extractFromOp(cls, o: OP, includeParams: List[Par] = None, excludeReadOnly=False):
		return cls(
			name=o.name,
			tox=o.par.externaltox.eval() if o.isCOMP else None,
			copyOf=_getParamSpec(o.par.clone) if o.isCOMP else None,
			pars=_extractParams(o, includeParams=includeParams, excludeReadOnly=excludeReadOnly),
		)

	@classmethod
	def fromDict(cls, d: dict):
		return cls(**d)

	def toDict(self, excludeKeys: List[str] = None):
		d = asdict(self)
		if 'master' in d:
			del d['master']
		if excludeKeys:
			d = {
				k: v
				for k, v in d.items()
				if k not in excludeKeys
			}
		return cleanDict(d)

	def saveSpecFile(self, file: Path):
		obj = self.toDict()
		with file.open(mode='w') as f:
			json.dump(obj, f, indent='  ')

	@classmethod
	def mergeSpecs(cls, *specs: 'ComponentSpec'):
		mergedDict = {}
		mergedPars = {}
		for spec in specs:
			if not spec:
				continue
			specDict = spec.toDict()
			if 'pars' in specDict:
				mergedPars.update(specDict['pars'])
				del specDict['pars']
			mergedDict.update(specDict)
		return cls(
			pars=mergedPars,
			**mergedDict,
		)

	def clone(self):
		return ComponentSpec(
			self.name,
			self.label,
			self.tox,
			dict(self.copyOf) if isinstance(self.copyOf, dict) else self.copyOf,
			dict(self.pars or {}),
			self.master,
		)

	def createComp(self, destination: COMP, resetDefault=False, includeParams: List[Par] = None) -> COMP:
		if self.copyOf and not self.master:
			if isinstance(self.copyOf, Dict):
				self.master = destination.evalExpression(self.copyOf['$'])
			else:
				self.master = destination.op(self.copyOf)
			if not self.master:
				raise Exception(f'Invalid component spec {self!r}')
		if self.master:
			comp = destination.copy(self.master, name=self.name)
		elif self.tox:
			comp = destination.loadTox(self.tox)
		else:
			raise Exception(f'Invalid component spec {self!r}')
		if self.name:
			comp.name = self.name
		elif self.tox:
			comp.name = Path(self.tox).stem
		# in case the name need to change for uniqueness, this will store the actual name
		self.name = comp.name
		self.applyParams(comp, resetDefault, includeParams)
		return comp

	def applyParams(self, comp: OP, resetDefault=False, includeParams: List[Par] = None):
		if self.tox:
			comp.par.externaltox = self.tox
		if not self.pars:
			return
		toReset = set((resetDefault and includeParams) or [])
		for name, val in self.pars.items():
			par = getattr(comp.par, name, None)
			if par is None:
				logger.warning(f'Param {name} not found in {comp}')
				continue
			if par.style == 'Header':
				continue
			if includeParams and par not in includeParams:
				continue
			if par in toReset:
				toReset.remove(par)
			if par.readOnly:
				continue
			_applyParamSetting(par, val, resetDefault=resetDefault)
		for par in toReset:
			par.val = par.default

def _applyParamSetting(par: 'Par', val: ValueOrExpr, resetDefault: bool):
	if par.readOnly:
		return
	if val is None:
		if resetDefault:
			par.val = par.default
			return
	if isinstance(val, dict):
		if '$' in val:
			par.expr = val['$']
		elif '@' in val:
			par.bindExpr = val['@']
		else:
			par.val = val
	else:
		par.val = val

def _extractParams(o: OP, includeParams: List[Par] = None, excludeReadOnly=False) -> _ParsT:
	pars = {}
	for par in o.customPars:
		if includeParams and par not in includeParams:
			continue
		if excludeReadOnly and par.readOnly:
			continue
		spec = _getParamSpec(par)
		if spec is not None:
			pars[par.name] = spec
	return pars

def _getParamSpec(par: Par) -> Optional[ValueOrExpr]:
	if par.mode == ParMode.EXPORT:
		return None
	if par.mode == ParMode.BIND:
		return {'@': par.bindExpr}
	if par.mode == ParMode.EXPRESSION:
		return {'$': par.expr}
	if par.isPulse or par.isMomentary:
		return None
	return par.eval()

@dataclass
class WorkspaceSpec:
	sceneFolder: Optional[str] = None

	# Defaults to *.tox
	sceneFilePattern: Optional[str] = None

	presetFolder: Optional[str] = None

	# Defaults to *.json
	presetFilePattern: Optional[str] = None

	autoRefreshFiles: bool = True

	settings: Dict[str, Dict[str, Any]] = field(default_factory=dict)

	def toObj(self, forFile: Optional[Path] = None):
		if forFile and self.sceneFolder and Path(self.sceneFolder) == forFile.parent:
			folder = None
		else:
			folder = self.sceneFolder
		return cleanDict({
			'sceneFolder': folder,
			'sceneFilePattern': self.sceneFilePattern,
			'presetFolder': self.presetFolder,
			'presetFilePattern': self.presetFilePattern,
			'autoRefreshFiles': self.autoRefreshFiles,
			'settings': self.settings or None,
		})

	def saveSpecFile(self, file: Path):
		obj = self.toObj(forFile=file)
		with file.open(mode='w') as f:
			json.dump(obj, f, indent='  ')

	@classmethod
	def fromObj(cls, obj: dict):
		return cls(**obj)

	@classmethod
	def fromFolder(cls, folder: Path):
		return cls(
			sceneFolder=folder.as_posix(),
		)

	@classmethod
	def fromSpecFile(cls, file: Path):
		with file.open(mode='r') as f:
			obj = json.load(f)
		spec = cls.fromObj(obj)
		if spec.sceneFolder is None:
			spec.sceneFolder = file.parent
		return spec

@dataclass
class WorkspaceItem:
	relPath: str = None
	name: str = None
	timestamp: Optional[int] = None

	isScene: bool = False
	isPreset: bool = False

@dataclass
class WorkspaceScene(WorkspaceItem):
	toxPath: str = None
	presets: List['WorkspacePreset'] = field(default_factory=list)
	isExpanded: bool = False

	isScene = True

@dataclass
class WorkspacePreset(WorkspaceItem):
	isPreset = True
	specPath: str = None
	sceneRelPath: str = None
