from dataclasses import dataclass, field
import json
from datetime import datetime
from pathlib import Path
import logging
from typing import Any, Dict, List, Optional, Union

from infraCommon import cleanDict

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from _typeAliases import *

	class _Par:
		Autorefresh: BoolParamT
	class _Comp(COMP):
		par = _Par()

	class _StatePar:
		Specfile: StrParamT
		Scenefolder: StrParamT
		Scenefilepattern: StrParamT
		Autoscenes: BoolParamT
		Loaded: BoolParamT
	ipar.workspaceState = _StatePar()

try:
	# noinspection PyUnresolvedReferences
	CallbacksExt = op.TDModules.op('TDCallbacksExt').module.CallbacksExt
except ImportError:
	from _stubs.TDCallbacksExt import CallbacksExt

workspaceFileName = 'index.json'
defaultSceneFileGlob = '*.tox'

logger = logging.Logger(__name__)

class Workspace(CallbacksExt):
	def __init__(self, ownerComp: 'COMP'):
		super().__init__(ownerComp)
		# noinspection PyTypeChecker
		self.ownerComp = ownerComp  # type: _Comp

	@staticmethod
	def Unloadworkspace(_=None):
		ipar.workspaceState.Specfile = ''
		ipar.workspaceState.Scenefolder = ''
		ipar.workspaceState.Autoscenes = True
		ipar.workspaceState.Scenefilepattern = '*.tox'
		ipar.workspaceState.Loaded = False

	def PromptLoadWorkspaceFile(self):
		path = ui.chooseFile(load=True, fileTypes=['json'], title='Open Workspace Spec File')
		if path:
			self.LoadWorkspaceFolder(path)

	def PromptLoadWorkspaceFolder(self):
		path = ui.chooseFolder(title='Open Workspace Folder')
		if path:
			self.LoadWorkspaceFolder(path)

	def LoadWorkspaceFolder(self, path: Union[Path, str]):
		folderPath = Path(path)
		ipar.workspaceState.Scenefolder = folderPath.as_posix()
		filePath = folderPath / workspaceFileName
		if filePath.exists():
			self.LoadWorkspaceFile(filePath)
		else:
			ipar.workspaceState.Specfile = ''
			spec = WorkspaceSpec.fromFolder(folderPath)
			self._loadWorkspaceSpec(spec)
			self._printStatus(f'Loaded workspace from folder {folderPath.as_posix()}')

	def LoadWorkspaceFile(self, path: Union[Path, str]):
		filePath = Path(path)
		ipar.workspaceState.Specfile = filePath.as_posix()
		spec = WorkspaceSpec.fromSpecFile(filePath)
		ipar.workspaceState.Scenefolder = Path(spec.sceneFolder).as_posix() if spec.sceneFolder else ''
		self._loadWorkspaceSpec(spec)
		self._printStatus(f'Loaded workspace from file {filePath.as_posix()}')

	def SaveWorkspaceFile(self, path: Union[None, Path, str]):
		if path is None:
			path = ipar.workspaceState.Specfile.eval()
			if not path and ipar.workspaceState.Scenefolder.eval():
				path = Path(ipar.workspaceState.Scenefolder.eval()) / workspaceFileName
			if not path:
				self._printStatus('Unable to save workspace! No spec file specified')
				return
		filePath = Path(path)
		ipar.workspaceState.Specfile = filePath.as_posix()
		spec = self._buildWorkspaceSpec()
		spec.saveSpecFile(filePath)

	def _loadWorkspaceSpec(self, spec: 'WorkspaceSpec'):
		ipar.workspaceState.Autoscenes = spec.autoScenes
		fileTable = self.ownerComp.op('manual_scene_files')  # type: tableDAT
		fileTable.clear()
		fileTable.appendRow(['name', 'basename', 'folder', 'path', 'relpath', 'datemodified', 'rawpath'])
		if not spec.autoScenes and spec.sceneFiles:
			sceneFolder = Path(spec.sceneFolder) if spec.sceneFolder else None
			for sceneFile in spec.sceneFiles:
				scenePath = Path(sceneFile)
				if sceneFolder and not scenePath.is_absolute():
					scenePath = sceneFolder / sceneFolder
				if not scenePath.exists():
					logger.warning(f'{self.ownerComp}: Scene file does not exist {sceneFile!r}')
					continue
				fileTable.appendRow([
					scenePath.name,
					scenePath.stem,
					scenePath.parent.as_posix(),
					scenePath.absolute().as_posix(),
					scenePath.as_posix(),
					scenePath.stat().st_mtime,
					sceneFile,
				])
		ipar.workspaceState.Loaded = True
		self._applySettings(spec.settings)

	def _buildWorkspaceSpec(self):
		spec = WorkspaceSpec(
			autoScenes=ipar.workspaceState.Autoscenes.eval(),
			sceneFolder=ipar.workspaceState.Scenefolder.eval() or '',
			sceneFilePattern=ipar.workspaceState.Scenefilepattern.eval() or '',
		)
		if not spec.autoScenes:
			spec.sceneFiles = []
			fileTable = self.ownerComp.op('manual_scene_files')
			if fileTable.numRows > 1 and fileTable[0, 'rawpath']:
				for cell in fileTable.col('rawpath')[1:]:
					spec.sceneFiles.append(cell.val)
		spec.settings = self._buildSettings()
		return spec

	def _applySettings(self, settings: Dict[str, Dict[str, Any]]):
		self.DoCallback('applySettings', {'settings': settings or {}})

	def _buildSettings(self) -> Dict[str, Dict[str, Any]]:
		resultInfo = self.DoCallback('buildSettings', {}) or {}
		return resultInfo.get('returnValue') or {}

	@staticmethod
	def prepareSceneTable(sceneTable: 'scriptDAT', sceneFileTable: 'tableDAT'):
		sceneTable.clear()
		sceneTable.appendRow([
			'relpath',
			'name',
			'modified',
			'timestamp',
			'tox',
		])
		if not ipar.workspaceState.Loaded:
			return
		for i in range(1, sceneFileTable.numRows):
			timestamp = float(sceneFileTable[i, 'datemodified'])
			path = str(sceneFileTable[i, 'path'])
			folder = str(sceneFileTable[i, 'folder'])
			modified = datetime.fromtimestamp(timestamp)
			if folder and not folder.endswith('/'):
				folder += '/'
			sceneTable.appendRow([
				path.replace(folder, '') if (folder and path.startswith(folder)) else path,
				sceneFileTable[i, 'basename'],
				int(timestamp),
				modified.strftime('%Y-%m-%d %H:%M'),
				path,
			])

	def _printStatus(self, msg):
		ui.status = msg
		print(self.ownerComp, msg)

	# Pulse param exec handlers

	def Loadworkspacefile(self, _=None):
		self.PromptLoadWorkspaceFile()

	def Loadworkspacefolder(self, _=None):
		self.PromptLoadWorkspaceFolder()

	def Saveworkspacefile(self, _=None):
		self.SaveWorkspaceFile()

@dataclass
class WorkspaceSpec:
	# If true, automatically scan sceneFolder to find scenes.
	# Otherwise rely on a predetermined list of sceneFiles
	autoScenes: Optional[bool] = None

	# For when the workspace uses a folder for scenes, or as
	# the root path when using sceneFiles
	sceneFolder: Optional[str] = None

	# Defaults to *.tox
	sceneFilePattern: Optional[str] = None

	# For when the workspace uses a list of scene files
	sceneFiles: Optional[List[str]] = None

	settings: Dict[str, Dict[str, Any]] = field(default_factory=dict)

	def __post_init__(self):
		if self.autoScenes is None:
			self.autoScenes = self.sceneFiles is None

	def toObj(self, forFile: Optional[Path] = None):
		if forFile and self.sceneFolder and Path(self.sceneFolder) == forFile.parent:
			folder = None
		else:
			folder = self.sceneFolder
		return cleanDict({
			'autoScenes': self.autoScenes,
			'sceneFolder': folder,
			'sceneFilePattern': self.sceneFilePattern,
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
			autoScenes=True,
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
