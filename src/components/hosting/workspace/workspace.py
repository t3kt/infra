import json
from datetime import datetime
from pathlib import Path
import logging
from typing import Any, Dict, Union

from infraHosting import WorkspaceSpec

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
		Loaded: BoolParamT
		Specfile: StrParamT

	class _SettingsPar:
		Scenefolder: StrParamT
		Scenefilepattern: StrParamT
		Presetfolder: StrParamT
		Presetfilepattern: StrParamT
		Autorefreshfiles: BoolParamT

	ipar.workspaceState = _StatePar()
	ipar.workspaceSettings = _SettingsPar()

try:
	# noinspection PyUnresolvedReferences
	CallbacksExt = op.TDModules.op('TDCallbacksExt').module.CallbacksExt
except ImportError:
	from _stubs.TDCallbacksExt import CallbacksExt

workspaceFileName = 'index.json'

logger = logging.Logger(__name__)

class Workspace(CallbacksExt):
	def __init__(self, ownerComp: 'COMP'):
		super().__init__(ownerComp)
		# noinspection PyTypeChecker
		self.ownerComp = ownerComp  # type: _Comp

	@staticmethod
	def Unloadworkspace(_=None):
		ipar.workspaceState.Loaded = False
		ipar.workspaceState.Specfile = ''
		ipar.workspaceSettings.Scenefolder = ''
		ipar.workspaceSettings.Scenefilepattern = '*.tox'
		ipar.workspaceSettings.Presetfolder = ''
		ipar.workspaceSettings.Presetfilepattern = '*.json'
		ipar.workspaceSettings.Autorefreshfiles = True

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
		ipar.workspaceSettings.Scenefolder = folderPath.as_posix()
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
		self._loadWorkspaceSpec(spec)
		self._printStatus(f'Loaded workspace from file {filePath.as_posix()}')

	def SaveWorkspaceFile(self, path: Union[None, Path, str] = None):
		if path is None:
			path = ipar.workspaceState.Specfile.eval()
			if not path and ipar.workspaceSettings.Scenefolder.eval():
				path = Path(ipar.workspaceSettings.Scenefolder.eval()) / workspaceFileName
			if not path:
				self._printStatus('Unable to save workspace! No spec file specified')
				return
		filePath = Path(path)
		ipar.workspaceSettings.Specfile = filePath.as_posix()
		spec = self._buildWorkspaceSpec()
		spec.saveSpecFile(filePath)

	def _loadWorkspaceSpec(self, spec: 'WorkspaceSpec'):
		ipar.workspaceSettings.Scenefolder = Path(spec.sceneFolder).as_posix() if spec.sceneFolder else ''
		self._applySettings(spec.settings)
		ipar.workspaceState.Loaded = True

	def _buildWorkspaceSpec(self):
		spec = WorkspaceSpec(
			sceneFolder=ipar.workspaceSettings.Scenefolder.eval() or '',
			sceneFilePattern=ipar.workspaceSettings.Scenefilepattern.eval() or '',
		)
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
			path = str(sceneFileTable[i, 'path'])
			sceneTable.appendRow([
				_formatRelPath(path, sceneFileTable[i, 'folder']),
				sceneFileTable[i, 'basename'],
				_formatDate(sceneFileTable[i, 'datemodified']),
				sceneFileTable[i, 'datemodified'],
				path,
			])

	def preparePresetTable(self, presetTable: 'scriptDAT', presetFileTable: 'tableDAT'):
		presetTable.clear()
		presetTable.appendRow([
			'relpath',
			'name',
			'scenerelpath',
			'modified',
			'timestamp',
			'path',
		])
		for i in range(1, presetFileTable.numRows):
			path = str(presetFileTable[i, 'path'])
			toxRelPath = self._loadAndExtractToxFromSpec(path)
			if not toxRelPath:
				self._printStatus(f'Skipping preset file without tox: {path}')
				continue
			presetTable.appendRow([
				_formatRelPath(path, presetFileTable[i, 'folder']),
				presetFileTable[i, 'basename'],
				toxRelPath or '',
				_formatDate(presetFileTable[i, 'datemodified']),
				presetFileTable[i, 'datemodified'],
				path,
			])

	def _printStatus(self, msg):
		ui.status = msg
		print(self.ownerComp, msg)

	def _loadAndExtractToxFromSpec(self, path: str):
		try:
			with Path(path).open(mode='r') as f:
				obj = json.load(f)
				return obj.get('tox')
		except Exception as e:
			self._printStatus(e)

	# Pulse param exec handlers

	def Loadworkspacefile(self, _=None):
		self.PromptLoadWorkspaceFile()

	def Loadworkspacefolder(self, _=None):
		self.PromptLoadWorkspaceFolder()

	def Saveworkspacefile(self, _=None):
		self.SaveWorkspaceFile()

def _formatDate(timestampCell):
	return datetime.fromtimestamp(float(timestampCell)).strftime('%Y-%m-%d %H:%M')

def _formatRelPath(pathCell, folderCell):
	folder = str(folderCell or '')
	if folder and not folder.endswith('/'):
		folder += '/'
	path = str(pathCell)
	return path.replace(folder, '') if (folder and path.startswith(folder)) else path
