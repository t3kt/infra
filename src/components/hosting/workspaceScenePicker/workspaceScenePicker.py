from dataclasses import dataclass
import logging
from typing import Dict, List, Optional, Union

from infraHosting import WorkspacePreset, WorkspaceScene

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from _typeAliases import *
	from ..workspace.workspace import Workspace

	# noinspection PyTypeHints
	iop.workspace = Workspace(COMP())  # type: Union[Workspace, COMP]

	class _SettingsPar:
		Showpresets: BoolParamT

	class _ListConfigPar:
		Bgcolorr: 'FloatParamT'
		Bgcolorg: 'FloatParamT'
		Bgcolorb: 'FloatParamT'

		Scenetextcolorr: 'FloatParamT'
		Scenetextcolorg: 'FloatParamT'
		Scenetextcolorb: 'FloatParamT'

		Scenebgcolorr: 'FloatParamT'
		Scenebgcolorg: 'FloatParamT'
		Scenebgcolorb: 'FloatParamT'

		Presettextcolorr: 'FloatParamT'
		Presettextcolorg: 'FloatParamT'
		Presettextcolorb: 'FloatParamT'

		Presetbgcolorr: 'FloatParamT'
		Presetbgcolorg: 'FloatParamT'
		Presetbgcolorb: 'FloatParamT'

		Rolloverhighlightcolorr: 'FloatParamT'
		Rolloverhighlightcolorg: 'FloatParamT'
		Rolloverhighlightcolorb: 'FloatParamT'

		Buttonbgcolorr: 'FloatParamT'
		Buttonbgcolorg: 'FloatParamT'
		Buttonbgcolorb: 'FloatParamT'

		Buttonrolloverbgcolorr: 'FloatParamT'
		Buttonrolloverbgcolorg: 'FloatParamT'
		Buttonrolloverbgcolorb: 'FloatParamT'

		Selectedhighlightcolorr: 'FloatParamT'
		Selectedhighlightcolorg: 'FloatParamT'
		Selectedhighlightcolorb: 'FloatParamT'

	ipar.pickerSettings = _SettingsPar()
	ipar.listConfig = _ListConfigPar()

try:
	# noinspection PyUnresolvedReferences
	CallbacksExt = op.TDModules.op('TDCallbacksExt').module.CallbacksExt
except ImportError:
	from _stubs.TDCallbacksExt import CallbacksExt

logger = logging.getLogger(__name__)

class WorkspaceScenePicker(CallbacksExt):
	def __init__(self, ownerComp: 'COMP'):
		super().__init__(ownerComp)
		self._itemCollection = _ItemCollection()
		self._selectedScene = None  # type: Optional[WorkspaceScene]
		self._selectedPreset = None  # type: Optional[WorkspacePreset]
		self._loadItems()

	@property
	def _listComp(self) -> 'listCOMP':
		return self.ownerComp.op('list')

	def _loadItems(self):
		sceneTable = self.ownerComp.op('scene_table')  # type: DAT
		presetTable = self.ownerComp.op('preset_table')  # type: DAT
		self._itemCollection.loadTables(sceneTable, presetTable)
		self._refreshList()

	def _refreshList(self):
		settings = _ViewSettings(
			showPresets=ipar.pickerSettings.Showpresets.eval(),
		)
		self._itemCollection.refreshDisplayItems(settings)
		listComp = self._listComp
		listComp.par.rows = len(self._itemCollection.displayItems)
		listComp.par.cols = 2
		listComp.par.reset.pulse()

	def _isSelectedItem(self, item: Optional['_AnyItemT']):
		if not item:
			return False
		if isinstance(item, WorkspacePreset):
			return item == self._selectedPreset
		if isinstance(item, WorkspaceScene):
			return item == self._selectedScene
		return False

	def list_onInitCell(self, row: int, col: int, attribs: 'ListAttributes'):
		item = self._itemCollection.itemForRow(row)
		if not item:
			return
		if col == 1:
			attribs.text = item.name
		if isinstance(item, WorkspaceScene):
			if col == 0:
				if ipar.pickerSettings.Showpresets and item.presets:
					if item.isExpanded:
						attribs.top = self.ownerComp.op('collapseIcon')
					else:
						attribs.top = self.ownerComp.op('expandIcon')
				attribs.bgColor = ipar.listConfig.Buttonbgcolorr, ipar.listConfig.Buttonbgcolorg, ipar.listConfig.Buttonbgcolorb, 1
			elif col == 1:
				attribs.textOffsetX = 5
		elif isinstance(item, WorkspacePreset):
			if col == 1:
				attribs.textOffsetX = 20

	def list_onInitRow(self, row: int, attribs: 'ListAttributes'):
		item = self._itemCollection.itemForRow(row)
		if not item:
			return
		if isinstance(item, WorkspaceScene):
			attribs.textColor = ipar.listConfig.Scenetextcolorr, ipar.listConfig.Scenetextcolorg, ipar.listConfig.Scenetextcolorb, 1
			attribs.bgColor = ipar.listConfig.Scenebgcolorr, ipar.listConfig.Scenebgcolorg, ipar.listConfig.Scenebgcolorb, 1
		elif isinstance(item, WorkspacePreset):
			attribs.textColor = ipar.listConfig.Presettextcolorr, ipar.listConfig.Presettextcolorg, ipar.listConfig.Presettextcolorb, 1
			attribs.bgColor = ipar.listConfig.Presetbgcolorr, ipar.listConfig.Presetbgcolorg, ipar.listConfig.Presetbgcolorb, 1
		self._setRowSelectedHighlight(row, self._isSelectedItem(item))

	def _setRowSelectedHighlight(self, row: int, selected: bool):
		self._setRowStatusHighlight(
			row, selected,
			(ipar.listConfig.Selectedhighlightcolorr, ipar.listConfig.Selectedhighlightcolorg, ipar.listConfig.Selectedhighlightcolorb, 1))

	def _setRowStatusHighlight(self, row: int, selected: bool, color: tuple):
		if row < 0:
			return
		if not selected:
			color = 0, 0, 0, 0
		listComp = self._listComp
		rowAttribs = listComp.rowAttribs[row]
		if rowAttribs:
			rowAttribs.topBorderOutColor = color
			rowAttribs.bottomBorderOutColor = color

	@staticmethod
	def list_onInitCol(col: int, attribs: 'ListAttributes'):
		if col == 0:
			attribs.colWidth = 26
		elif col == 1:
			attribs.colStretch = True

	@staticmethod
	def list_onInitTable(attribs: 'ListAttributes'):
		attribs.rowHeight = 26
		attribs.fontFace = 'Roboto'
		attribs.fontSizeX = 18
		attribs.textJustify = JustifyType.CENTERLEFT
		attribs.bgColor = ipar.listConfig.Bgcolorr, ipar.listConfig.Bgcolorg, ipar.listConfig.Bgcolorb, 1

	def _toggleExpansion(
			self,
			item: WorkspaceScene):
		item.isExpanded = not item.isExpanded
		self._refreshList()

	def _selectScene(self, scene: Optional[WorkspaceScene], quiet: bool):
		self._updateSelection(scene, None, quiet=quiet)

	def _selectPreset(self, preset: Optional[WorkspacePreset], quiet: bool):
		scene = self._itemCollection.getSceneByTox(preset.sceneRelPath) if preset else None
		self._updateSelection(scene, preset, quiet=quiet)

	def _updateSelection(
			self,
			scene: WorkspaceScene,
			preset: Optional[WorkspacePreset],
			quiet: bool
	):
		self._selectedScene = scene
		self._selectedPreset = preset
		self._refreshList()
		if not quiet:
			self.DoCallback('onSelectionChange', {
				'scene': scene,
				'preset': preset,
			})

	def list_onSelect(self, endRow: int, endCol: int, end: bool):
		if not end:
			return
		item = self._itemCollection.itemForRow(endRow)
		if not item:
			return
		if isinstance(item, WorkspaceScene):
			if endCol == 0 and item.presets and ipar.pickerSettings.Showpresets:
				self._toggleExpansion(item)
			else:
				self._selectScene(item, quiet=False)
		elif isinstance(item, WorkspacePreset):
			self._selectPreset(item, quiet=False)

	def SelectScene(
			self,
			toxRelPath: Optional[str] = None,
			scene: Optional[WorkspaceScene] = None,
			quiet: bool = False,
	) -> Optional[WorkspaceScene]:
		if scene:
			if toxRelPath:
				raise Exception('Cannot specify both a scene and toxRelPath')
		else:
			if not toxRelPath:
				raise Exception('Must specify either a scene or toxRelPath')
			scene = self._itemCollection.getSceneByTox(toxRelPath)
		if not scene:
			return None
		self._selectScene(scene, quiet)
		return scene

	def SelectPreset(
			self,
			preset: Optional[WorkspacePreset] = None,
			presetRelPath: Optional[str] = None,
			quiet: bool = False,
	):
		if preset:
			if presetRelPath:
				raise Exception('Cannot specify both a preset and presetRelPath')
		else:
			if not presetRelPath:
				raise Exception('Must specify either a preset or presetRelPath')
			preset = self._itemCollection.getPresetByPath(presetRelPath)
		if not preset:
			return None
		self._selectPreset(preset, quiet)
		return preset

	def DeselectScene(self, quiet: bool = False):
		self._selectScene(None, quiet)

	def DeselectPreset(self, quiet: bool = False):
		self._selectPreset(None, quiet)

@dataclass
class _ViewSettings:
	showPresets: bool = True
	sortBy: str = 'path'

_AnyItemT = Union[WorkspaceScene, WorkspacePreset]

class _ItemCollection:
	scenes: List[WorkspaceScene]
	presets: List[WorkspacePreset]
	displayItems: Optional[List[_AnyItemT]]

	def __init__(self):
		self.scenes = []
		self.presets = []
		self.displayItems = []

	def loadTables(
			self,
			sceneTable: 'DAT', presetTable: 'DAT',
	):
		self.scenes = []
		self.presets = []
		self.displayItems = []
		scenesByTox = {}  # type: Dict[str, WorkspaceScene]

		# relpath
		# name
		# modified
		# timestamp
		# tox
		for sceneRow in range(1, sceneTable.numRows):
			timestamp = sceneTable[sceneRow, 'timestamp']
			scene = WorkspaceScene(
				relPath=str(sceneTable[sceneRow, 'relpath']),
				name=str(sceneTable[sceneRow, 'name']),
				timestamp=int(timestamp) if timestamp is not None else None,
				toxPath=str(sceneTable[sceneRow, 'tox']),
			)
			self.scenes.append(scene)
			scenesByTox[scene.relPath] = scene

		# relpath
		# name
		# scenerelpath
		# modified
		# timestamp
		# path
		for presetRow in range(1, presetTable.numRows):
			timestamp = sceneTable[presetRow, 'timestamp']
			preset = WorkspacePreset(
				relPath=str(presetTable[presetRow, 'relpath']),
				name=str(presetTable[presetRow, 'name']),
				sceneRelPath=str(presetTable[presetRow, 'scenerelpath']),
				timestamp=int(timestamp) if timestamp is not None else None,
				specPath=str(presetTable[presetRow, 'path']),
			)
			scene = scenesByTox.get(preset.sceneRelPath)
			if not scene:
				logger.warning(f'Skipping preset for missing scene: {preset}')
			else:
				scene.presets.append(preset)
				self.presets.append(preset)

	def getSceneByTox(self, toxPath: str) -> Optional[WorkspaceScene]:
		for scene in self.scenes:
			if scene.relPath == toxPath:
				return scene

	def getPresetByPath(self, presetRelPath: str) -> Optional[WorkspacePreset]:
		for preset in self.presets:
			if preset.relPath == presetRelPath:
				return preset

	def addScene(self, scene: WorkspaceScene):
		self.scenes.append(scene)
		for preset in (scene.presets or []):
			self.presets.append(preset)

	def addPreset(self, preset: WorkspacePreset):
		scene = self.getSceneByTox(preset.sceneRelPath)
		if not scene:
			raise Exception(f'Scene not found for preset, tox: {preset.sceneRelPath!r}')
		scene.presets.append(preset)
		self.presets.append(preset)

	def refreshDisplayItems(self, settings: Optional[_ViewSettings]):
		settings = settings or _ViewSettings()
		self.displayItems = []

		# if settings.sortBy == 'name':
		def _sortKey(item: _AnyItemT): return item.relPath

		for scene in sorted(self.scenes, key=_sortKey):
			self.displayItems.append(scene)
			if settings.showPresets and scene.presets and scene.isExpanded:
				for preset in sorted(scene.presets, key=_sortKey):
					self.displayItems.append(preset)

	def itemForRow(self, row: int) -> Optional[_AnyItemT]:
		items = self.displayItems
		if not items or row < 0 or row >= len(items):
			return None
		return items[row]

	def rowForItem(self, item: Optional[_AnyItemT]) -> int:
		if not item:
			return -1
		items = self.displayItems
		if not items:
			return -1
		try:
			return items.index(item)
		except ValueError:
			return -1
