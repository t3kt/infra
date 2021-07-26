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
	ipar.pickerSettings = _SettingsPar()

try:
	# noinspection PyUnresolvedReferences
	CallbacksExt = op.TDModules.op('TDCallbacksExt').module.CallbacksExt
except ImportError:
	from _stubs.TDCallbacksExt import CallbacksExt

logger = logging.getLogger(__name__)

class WorkspaceScenePicker(CallbacksExt):
	def __init__(self, ownerComp: 'COMP'):
		super(CallbacksExt).__init__(ownerComp)
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
		raise NotImplementedError()

	def list_onInitCell(self, row: int, col: int, attribs: 'ListAttributes'):
		item = self._itemCollection.itemForRow(row)
		if not item:
			return
		if col == 1:
			attribs.text = item.name
		if item.isScene:
			if col == 0:
				if ipar.pickerSettings.Showpresets and item.presets:
					if item.isExpanded:
						attribs.top = self.ownerComp.op('collapseIcon')
					else:
						attribs.top = self.ownerComp.op('expandIcon')
			elif col == 1:
				attribs.textOffsetX = 5
		elif item.isPreset:
			if col == 1:
				attribs.textOffsetX = 20

	def list_onInitRow(self, row: int, attribs: 'ListAttributes'):
		item = self._itemCollection.itemForRow(row)
		if not item:
			return
		pass

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
