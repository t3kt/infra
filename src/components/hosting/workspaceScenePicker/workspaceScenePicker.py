from dataclasses import dataclass
import logging
from typing import Dict, List, Optional, Union

from infraHosting import WorkspaceItem, WorkspacePreset, WorkspaceScene

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from ..workspace.workspace import Workspace

	# noinspection PyTypeHints
	iop.workspace = Workspace(COMP())  # type: Union[Workspace, COMP]

try:
	# noinspection PyUnresolvedReferences
	CallbacksExt = op.TDModules.op('TDCallbacksExt').module.CallbacksExt
except ImportError:
	from _stubs.TDCallbacksExt import CallbacksExt

logger = logging.getLogger(__name__)

class WorkspaceScenePicker(CallbacksExt):
	def __init__(self, ownerComp: 'COMP'):
		super(CallbacksExt).__init__(ownerComp)
		self.itemCollection = _ItemCollection()
		self._loadItems()

	def _loadItems(self):
		pass

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
	def _currentItemList(self):
		return self.displayItems if self.displayItems is not None else self.allItems

	@property
	def _currentItemCount(self):
		return len(self._currentItemList)

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
		items = self._currentItemList
		if not items or row < 0 or row >= len(items):
			return None
		return items[row]

	def rowForItem(self, item: Optional[_AnyItemT]) -> int:
		if not item:
			return -1
		items = self._currentItemList
		if not items:
			return -1
		try:
			return items.index(item)
		except ValueError:
			return -1
