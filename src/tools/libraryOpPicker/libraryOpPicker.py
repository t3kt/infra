from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

from TDCallbacksExt import CallbacksExt

class LibraryOpPicker(CallbacksExt):
	def __init__(self, ownerComp: 'COMP'):
		super().__init__(ownerComp)

@dataclass
class PickerItem:
	shortName: str = None
	path: Optional[str] = None
	relPath: Optional[str] = None
	packageId: Optional[str] = None

	isPackage: bool = False
	isComp: bool = False

@dataclass
class PickerPackageItem(PickerItem):
	comps: List['PickerCompItem'] = field(default_factory=list)
	ixExpanded: bool = True

	isPackage: bool = True

@dataclass
class PickerCompItem(PickerItem):
	opType: Optional[str] = None
	tags: List[str] = field(default_factory=list)
	status: Optional[str] = None

	isComp: bool = True

_AnyItemT = Union[PickerPackageItem, PickerCompItem]

@dataclass
class _ViewSettings:
	text: Optional[str] = None
	hideStatuses: List[str] = field(default_factory=list)

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
			relPath = packageTable[i, 'relPath'].val
			comp = PickerCompItem(
				shortName=compTable[i, 'shortName'].val,
				path=pathPrefix + relPath,
				relPath=relPath,
				packageId=compTable[i, 'packageId'].val,
				opType=compTable[i, 'opType'].val,
				tags=tdu.split(compTable[i, 'tags']),
				status=compTable[i, 'status'].val,
			)
			package = packagesById.get(comp.packageId)
			if package:
				package.comps.append(comp)
				# don't include comps without packages
				self.comps.append(comp)

	def refreshDisplayItems(self, settings: Optional[_ViewSettings]):
		settings = settings or _ViewSettings()
		self.displayItems = []
		raise NotImplementedError()
		pass
