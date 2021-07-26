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
logger.setLevel(logging.DEBUG)

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
		self._applyViewSettings()
		self._refreshList()

	def _refreshList(self):
		listComp = self._listComp
		listComp.par.rows = len(self._itemCollection.currentItemList)
		listComp.par.cols = 2
		listComp.par.reset.pulse()

	def _applyViewSettings(self):
		settings = _ViewSettings(
			showPresets=ipar.pickerSettings.Showpresets.eval(),
		)
		self._itemCollection.applyViewSettings(settings)
		self._refreshList()

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
		self._applyViewSettings()

	def _selectScene(self, scene: Optional[WorkspaceScene], quiet: bool):
		self._updateSelection(scene, None, quiet=quiet)

	def _selectPreset(self, preset: Optional[WorkspacePreset], quiet: bool):
		scene = self._itemCollection.getSceneForPreset(preset) if preset else None
		self._updateSelection(scene, preset, quiet=quiet)

	def _updateSelection(
			self,
			scene: WorkspaceScene,
			preset: Optional[WorkspacePreset],
			quiet: bool
	):
		self._selectedScene = scene
		self._selectedPreset = preset
		self._applyViewSettings()
		if not quiet:
			self.DoCallback('onSelectionChange', {
				'scene': scene,
				'preset': preset,
			})

	def list_onSelect(self, endRow: int, endCol: int, end: bool):
		print(f'list_onSelect endRow: {endRow} endCol: {endCol} end: {end}')
		if not end:
			return
		item = self._itemCollection.itemForRow(endRow)
		print(f'.... item: {item!r}')
		if not item:
			return
		if isinstance(item, WorkspaceScene):
			if endCol == 0 and item.presets and ipar.pickerSettings.Showpresets:
				print('...... toggle expansion')
				self._toggleExpansion(item)
			else:
				print('..... select scene')
				self._selectScene(item, quiet=False)
		elif isinstance(item, WorkspacePreset):
			self._selectPreset(item, quiet=False)

@dataclass
class _ViewSettings:
	showPresets: bool = True

_AnyItemT = Union[WorkspaceScene, WorkspacePreset]

class _ItemCollection:
	allItems: List[_AnyItemT]
	scenes: List[WorkspaceScene]
	presets: List[WorkspacePreset]
	displayItems: Optional[List[_AnyItemT]]

	def __init__(self):
		self.allItems = []
		self.scenes = []
		self.presets = []
		self.displayItems = None

	@property
	def currentItemList(self):
		return self.displayItems if self.displayItems is not None else self.allItems

	def loadTables(self, sceneTable: 'DAT', presetTable: 'DAT'):
		self.allItems = []
		self.scenes = []
		self.presets = []
		self.displayItems = None
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
			scenesByTox[scene.toxPath] = scene

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

		self.allItems = self._buildFlatList(None)

	def getSceneForPreset(self, preset: WorkspacePreset):
		for scene in self.scenes:
			if scene.toxPath == preset.sceneRelPath:
				return scene

	def _buildFlatList(self, settings: Optional[_ViewSettings]):
		settings = settings or _ViewSettings()
		items = []
		for scene in self.scenes:
			items.append(scene)
			if settings.showPresets and scene.presets and scene.isExpanded:
				for preset in scene.presets:
					items.append(preset)
		return items

	def applyViewSettings(self, settings: Optional[_ViewSettings]):
		self.displayItems = self._buildFlatList(settings)

	def itemForRow(self, row: int) -> Optional[_AnyItemT]:
		items = self.currentItemList
		if not items or row < 0 or row >= len(items):
			return None
		return items[row]

	def rowForItem(self, item: Optional[_AnyItemT]) -> int:
		if not item:
			return -1
		items = self.currentItemList
		if not items:
			return -1
		try:
			return items.index(item)
		except ValueError:
			return -1
