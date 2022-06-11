from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from _typeAliases import *

	class _PickerPar:
		Libraryroot: OPParamT
		Rowheight: IntParamT
		Callbackdat: OPParamT
	class _PickerComp(COMP):
		par: _PickerPar

	class _UiStatePar:
		Searchtext: StrParamT
		Hidestatuses: StrParamT
	ipar.uiState = _UiStatePar()

	class _ListConfigPar(ParCollection):
		Bgcolorr: 'FloatParamT'
		Bgcolorg: 'FloatParamT'
		Bgcolorb: 'FloatParamT'

		Textcolorr: 'FloatParamT'
		Textcolorg: 'FloatParamT'
		Textcolorb: 'FloatParamT'

		Alphacolorr: 'FloatParamT'
		Alphacolorg: 'FloatParamT'
		Alphacolorb: 'FloatParamT'

		Betacolorr: 'FloatParamT'
		Betacolorg: 'FloatParamT'
		Betacolorb: 'FloatParamT'

		Deprecatedcolorr: 'FloatParamT'
		Deprecatedcolorg: 'FloatParamT'
		Deprecatedcolorb: 'FloatParamT'

		Rolloverhighlightcolorr: 'FloatParamT'
		Rolloverhighlightcolorg: 'FloatParamT'
		Rolloverhighlightcolorb: 'FloatParamT'

		Groupbgcolorr: 'FloatParamT'
		Groupbgcolorg: 'FloatParamT'
		Groupbgcolorb: 'FloatParamT'

		Grouptextcolorr: 'FloatParamT'
		Grouptextcolorg: 'FloatParamT'
		Grouptextcolorb: 'FloatParamT'

		Buttonbgcolorr: 'FloatParamT'
		Buttonbgcolorg: 'FloatParamT'
		Buttonbgcolorb: 'FloatParamT'

		Buttonrolloverbgcolorr: 'FloatParamT'
		Buttonrolloverbgcolorg: 'FloatParamT'
		Buttonrolloverbgcolorb: 'FloatParamT'
	ipar.listConfig = _ListConfigPar()

from TDCallbacksExt import CallbacksExt

class LibraryOpPicker(CallbacksExt):
	def __init__(self, ownerComp: 'COMP'):
		super().__init__(ownerComp)
		# noinspection PyTypeChecker
		self.ownerComp = ownerComp  # type: _PickerComp
		self._selItem = tdu.Dependency()  # value type: _AnyItemT
		self._itemCollection = _ItemCollection()
		if self.ownerComp.par.Libraryroot:
			pass
		self._loadItems()

	@property
	def _listComp(self) -> 'listCOMP':
		return self.ownerComp.op('list')

	@property
	def SelectedItem(self) -> Optional['_AnyItemT']:
		return self._selItem.val

	@property
	def _showEdit(self):
		# TODO: edit button stuff
		return False

	def _loadItems(self):
		packageTable = self.ownerComp.op('packageTable')
		componentTable = self.ownerComp.op('componentTable')
		self._itemCollection.loadTables(
			packageTable,
			componentTable,
			self.ownerComp.par.Libraryroot.eval())
		self._applyFilter()
		self._refreshList()

	def _refreshList(self):
		listComp = self._listComp
		listComp.par.rows = len(self._itemCollection.displayItems)
		listComp.par.cols = 3  # TODO: maybe have toggle for edit buttons?
		listComp.par.reset.pulse()
		self.DoCallback('onListRefresh', {
			'picker': self,
			'listComp': self._listComp,
			'rowHeight': self.ownerComp.par.Rowheight,
		})

	def _applyFilter(self):
		item = self.SelectedItem
		settings = _ViewSettings(
			searchText=ipar.uiState.Searchtext.eval(),
			hideStatuses=tdu.split(ipar.uiState.Hidestatuses),
		)
		self._itemCollection.refreshDisplayItems(settings)
		if item:
			row = self._itemCollection.rowForItem(item)
			if row < 0:
				self._selectItem(None, scroll=False)

	def _selectItem(self, item: Optional['_AnyItemT'], scroll: bool):
		oldItem = self.SelectedItem
		if oldItem == item:
			return
		if oldItem:
			row = self._itemCollection.rowForItem(oldItem)
			self._setRowHighlight(row, False)
		self._selItem.val = item
		if item:
			row = self._itemCollection.rowForItem(item)
			self._setRowHighlight(row, True)
			if scroll:
				self._listComp.scroll(row, 0)

	def ResetState(self):
		self._clearFilterText()
		self._applyFilter()
		self._refreshList()
		self._selectItem(None, scroll=False)

	def Resetstate(self, _=None):
		self.ResetState()

	def _setAllExpanded(self, expanded: bool):
		self._itemCollection.setAllExpansion(expanded)
		self._applyFilter()
		self._refreshList()

	def Expandall(self, _=None):
		self._setAllExpanded(False)  # not sure why this shouldn't be True...

	def Collapseall(self, _=None):
		self._setAllExpanded(True)

	def _clearFilterText(self):
		# TODO: clear filter text
		pass

	def onPickItem(self):
		item = self.SelectedItem
		if not item:
			item = self._itemCollection.firstCompItem()
			if not item:
				return
			else:
				self._selectItem(item, scroll=False)
		self.DoCallback('onPickItem', {
			'picker': self,
			'item': item,
		})

	def onEditItem(self):
		item = self.SelectedItem
		if not item:
			return
		self.DoCallback('onEditItem', {
			'picker': self,
			'item': item,
		})

	def list_onInitCell(self, row: int, col: int, attribs: 'ListAttributes'):
		item = self._itemCollection.itemForRow(row)
		if not item:
			return
		if col == 1:
			attribs.text = item.shortName
		if item.isPackage:
			if col == 0:
				attribs.top = self.ownerComp.op('expandIcon' if item.isExpanded else 'collapseIcon')
				attribs.bgColor = ipar.listConfig.Buttonbgcolorr, ipar.listConfig.Buttonbgcolorg, ipar.listConfig.Buttonbgcolorb, 1
			elif col == 1:
				attribs.textOffsetX = 5
		elif item.isComp:
			if col == 1:
				attribs.textOffsetX = 20
			elif col == 2:
				if item.isAlpha:
					attribs.top = self.ownerComp.op('alphaIcon')
				elif item.isBeta:
					attribs.top = self.ownerComp.op('betaIcon')
				elif item.isDeprecated:
					attribs.top = self.ownerComp.op('deprecatedIcon')
			elif col == 3:
				# TODO: edit icon button
				pass

	def list_onInitRow(self, row: int, attribs: 'ListAttributes'):
		item = self._itemCollection.itemForRow(row)
		if not item:
			return
		if item.isAlpha or item.isBeta or item.isDeprecated:
			attribs.fontItalic = True
		if item.isPackage:
			attribs.textColor = ipar.listConfig.Grouptextcolorr, ipar.listConfig.Grouptextcolorg, ipar.listConfig.Grouptextcolorb, 1
			attribs.bgColor = ipar.listConfig.Groupbgcolorr, ipar.listConfig.Groupbgcolorg, ipar.listConfig.Groupbgcolorb, 1
		elif item.isComp:
			if item.isAlpha:
				attribs.textColor = ipar.listConfig.Alphacolorr, ipar.listConfig.Alphacolorg, ipar.listConfig.Alphacolorb, 1
			if item.isAlpha:
				attribs.textColor = ipar.listConfig.Alphacolorr, ipar.listConfig.Alphacolorg, ipar.listConfig.Alphacolorb, 1
			elif item.isBeta:
				attribs.textColor = ipar.listConfig.Betacolorr, ipar.listConfig.Betacolorg, ipar.listConfig.Betacolorb, 1
			elif item.isDeprecated:
				attribs.textColor = ipar.listConfig.Deprecatedcolorr, ipar.listConfig.Deprecatedcolorg, ipar.listConfig.Deprecatedcolorb, 1

	@staticmethod
	def list_onInitCol(col: int, attribs: 'ListAttributes'):
		if col == 0:
			attribs.colWidth = 26
		elif col == 1:
			attribs.colStretch = True
		elif col == 2:
			attribs.colWidth = 30
		elif col == 3:
			attribs.colWidth = 26

	def list_onInitTable(self, attribs: 'ListAttributes'):
		attribs.rowHeight = self.ownerComp.par.Rowheight
		attribs.bgColor = ipar.listConfig.Bgcolorr, ipar.listConfig.Bgcolorg, ipar.listConfig.Bgcolorb
		attribs.textColor = ipar.listConfig.Textcolorr, ipar.listConfig.Textcolorg, ipar.listConfig.Textcolorb
		attribs.fontFace = 'Roboto'
		attribs.fontSizeX = 18
		attribs.textJustify = JustifyType.CENTERLEFT

	def _setButtonHighlight(self, row: int, col: int, highlight: bool):
		if row < 0 or col < 0:
			return
		attribs = self._listComp.cellAttribs[row, col]
		if not attribs:
			return
		if highlight:
			color = ipar.listConfig.Buttonrolloverbgcolorr, ipar.listConfig.Buttonrolloverbgcolorg, ipar.listConfig.Buttonrolloverbgcolorb, 1
		else:
			color = ipar.listConfig.Buttonbgcolorr, ipar.listConfig.Buttonbgcolorg, ipar.listConfig.Buttonbgcolorb, 1
		attribs.bgColor = color

	def _setRowHighlight(self, row: int, selected: bool):
		if row < 0:
			return
		# print(self.ownerComp, f'setRowHighlight(row: {row!r}, sel: {selected!r})')
		if selected:
			color = ipar.listConfig.Rolloverhighlightcolorr, ipar.listConfig.Rolloverhighlightcolorg, ipar.listConfig.Rolloverhighlightcolorb, 1
		else:
			color = 0, 0, 0, 0
		listComp = self._listComp
		rowAttribs = listComp.rowAttribs[row]
		if rowAttribs:
			rowAttribs.topBorderOutColor = color
			rowAttribs.bottomBorderOutColor = color
		cellAttribs = listComp.cellAttribs[row, 0]
		if cellAttribs:
			cellAttribs.leftBorderInColor = color
		cellAttribs = listComp.cellAttribs[row, 3 if self._showEdit else 2]
		if cellAttribs:
			cellAttribs.rightBorderOutColor = color

	def onRollover(
			self,
			row: int, col: int,
			prevRow: int, prevCol: int):
		# note for performance: this gets called frequently as the mouse moves even within a single cell
		if row == prevRow and col == prevCol:
			return
		if row >= 0:
			item = self._itemCollection.itemForRow(row)
			self._selectItem(item, scroll=False)
			if col == 3 and item.isComp:
				self._setButtonHighlight(row, col, True)
		if prevRow >= 0 and prevCol == 3:
			item = self._itemCollection.itemForRow(prevRow)
			if item.isComp:
				self._setButtonHighlight(prevRow, prevCol, False)

	def _togglePackageExpansion(self, item: 'PickerPackageItem'):
		item.isExpanded = not item.isExpanded
		self._applyFilter()
		self._refreshList()
		if item.isExpanded:
			self._selectItem(item.comps[0] if item.comps else None, scroll=False)
		else:
			self._selectItem(item, scroll=False)

	def list_onSelect(self, endRow: int, endCol: int, end: bool):
		item = self._itemCollection.itemForRow(endRow)
		# print(self.ownerComp, f'SELECT startRC: {startRow},{startCol}, endRC: {endRow},{endCol}, start: {start}, end: {end} \n{item}')
		self._selectItem(item, scroll=False)
		if end:
			if item.isPackage:
				self._togglePackageExpansion(item)
			elif endCol == 3 and self._showEdit:
				self.onEditItem()
			else:
				self.onPickItem()

	def Createcallbacks(self, _=None):
		par = self.ownerComp.par.Callbackdat
		if par.eval():
			return
		ui.undo.startBlock('Create callbacks')
		dat = self.ownerComp.parent().create(textDAT, self.ownerComp.name + '_callbacks')
		dat.copy(self.ownerComp.op('callbacksTemplate'))
		dat.par.extension = 'py'
		dat.nodeX = self.ownerComp.nodeX
		dat.nodeY = self.ownerComp.nodeY - 150
		dat.dock = self.ownerComp
		self.ownerComp.showDocked = True
		dat.viewer = True
		par.val = dat
		ui.undo.endBlock()

@dataclass
class PickerItem:
	shortName: str = None
	path: Optional[str] = None
	relPath: Optional[str] = None
	packageId: Optional[str] = None

	isAlpha: bool = False
	isBeta: bool = False
	isDeprecated: bool = False

	isPackage: bool = False
	isComp: bool = False

@dataclass
class PickerPackageItem(PickerItem):
	comps: List['PickerCompItem'] = field(default_factory=list)
	isExpanded: bool = True

	isPackage: bool = True

@dataclass
class PickerCompItem(PickerItem):
	opType: Optional[str] = None
	tags: List[str] = field(default_factory=list)
	status: Optional[str] = None
	words: List[str] = field(default_factory=list)

	isComp: bool = True

	def matchesFilter(self, settings: '_ViewSettings'):
		if settings.hideStatuses and self.status in settings.hideStatuses:
			return False
		if not settings.searchText:
			return True
		if settings.searchText in self.shortName.lower():
			return True
		return _searchMatchesWords(settings.searchText, self.words)

_AnyItemT = Union[PickerPackageItem, PickerCompItem]

@dataclass
class _ViewSettings:
	searchText: Optional[str] = None
	hideStatuses: List[str] = field(default_factory=list)

	def __post_init__(self):
		if self.searchText:
			self.searchText = self.searchText.lower().strip()

	def hasAnyFilters(self):
		return bool(self.searchText or self.hideStatuses)

class _ItemCollection:
	packages: List[PickerPackageItem]
	comps: List[PickerCompItem]
	displayItems: List[_AnyItemT]

	def __init__(self):
		self.packages = []
		self.comps = []
		self.displayItems = []


	def loadTables(
			self,
			packageTable: 'DAT',
			compTable: 'DAT',
			libraryRoot: 'COMP'):
		self.packages = []
		self.comps = []
		self.displayItems = []
		packagesById = {}  # type: Dict[str, PickerPackageItem]

		pathPrefix = libraryRoot.path + '/'
		# packageId
		# path
		# relPath
		# depth
		for i in range(1, packageTable.numRows):
			relPath = packageTable[i, 'relPath'].val
			package = PickerPackageItem(
				shortName=relPath,
				path=pathPrefix + relPath,
				relPath=relPath,
				packageId=packageTable[i, 'packageId'].val,
				isExpanded=True,
			)
			self.packages.append(package)
			packagesById[package.packageId] = package

		# opType
		# shortName
		# fullName
		# path
		# relPath
		# packageId
		# tags
		# opVersion
		# opStatus
		for i in range(1, compTable.numRows):
			relPath = compTable[i, 'relPath'].val
			shortName = compTable[i, 'shortName'].val
			status = compTable[i, 'opStatus'].val
			comp = PickerCompItem(
				shortName=shortName,
				path=pathPrefix + relPath,
				relPath=relPath,
				packageId=compTable[i, 'packageId'].val,
				opType=compTable[i, 'opType'].val,
				tags=tdu.split(compTable[i, 'tags']),
				status=status,
				isAlpha=status == 'alpha',
				isBeta=status == 'beta',
				isDeprecated=status == 'deprecated',
				words=[w.lower() for w in _splitCamelCase(shortName)],
			)
			package = packagesById.get(comp.packageId)
			if package:
				package.comps.append(comp)
				# don't include comps without packages
				self.comps.append(comp)

	def setAllExpansion(self, expanded: bool):
		for package in self.packages:
			package.isExpanded = expanded

	def refreshDisplayItems(self, settings: Optional[_ViewSettings]):
		settings = settings or _ViewSettings()
		self.displayItems = []

		def _sortKey(item: _AnyItemT): return item.relPath

		hasFilter = settings.hasAnyFilters()
		for package in sorted(self.packages, key=_sortKey):
			if not package or not package.comps:
				continue
			if not hasFilter:
				matchedComps = package.comps
			else:
				matchedComps = [c for c in package.comps if c.matchesFilter(settings)]
			if matchedComps:
				self.displayItems.append(package)
				if not package.isExpanded:
					self.displayItems += matchedComps

	def itemForRow(self, row: int) -> Optional[_AnyItemT]:
		items = self.displayItems
		if not items or row < 0 or row >= len(items):
			return None
		return items[row]

	def rowForItem(self, item: Optional[_AnyItemT]) -> int:
		if not item or not self.displayItems:
			return -1
		try:
			return self.displayItems.index(item)
		except ValueError:
			return -1

	def firstCompItem(self) -> Optional[PickerCompItem]:
		for item in self.displayItems:
			if item.isComp:
				return item

def _splitCamelCase(s: str):
	splits = [i for i, e in enumerate(s) if e.isupper() or e.isdigit()] + [len(s)]
	if not splits:
		return [s]
	splits = [0] + splits
	return [s[x:y] for x, y in zip(splits, splits[1:])]

def _searchMatchesWords(search: str, words: List[str]):
	if not words or len(search) > len(words):
		return False
	if any(w.startswith(search) for w in words):
		return True
	for w, s in zip(words, search):
		if w[0] != s:
			return False
	return True
