from dataclasses import dataclass
from typing import Optional, Union, List

from infraCommon import mergeDicts
from infraData import DataObjectBase

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from _typeAliases import *
	from TDCallbacksExt import CallbacksExt

	class _MetaParsT(ParCollection):
		Hostop: 'OPParamT'
		Helpurl: 'StrParamT'
		Helpdat: 'OPParamT'
		Libraryname: 'StrParamT'
		Libraryversion: 'StrParamT'

	class _CompMetaParsT(_MetaParsT):
		Optype: 'StrParamT'
		Opversion: 'StrParamT'
		Opstatus: 'StrParamT'

	class _CompMetaCompT(COMP):
		par: _CompMetaParsT

	class _PackageMetaParsT(_MetaParsT):
		Packageid: 'StrParamT'

	class _PackageMetaCompT(COMP):
		par: _PackageMetaParsT

	class _LibraryMetaParsT(_MetaParsT):
		Packageroot: OPParamT
		Packagetags: StrParamT
		Componenttags: StrParamT
		Metafilesuffix: StrParamT

	class _LibraryMetaCompT(COMP):
		par: _LibraryMetaParsT

class CompInfo:
	comp: 'Optional[AnyOpT]'
	metaComp: 'Optional[_CompMetaCompT]'
	metaPar: 'Optional[_CompMetaParsT]'

	def __init__(self, o: 'Union[OP, str, Cell, Par]'):
		o = op(o)
		if not o or not o.isCOMP:
			return
		if _isCompMeta(o.op('componentMeta')):
			self.comp = o
			# noinspection PyTypeChecker
			self.metaComp = o.op('componentMeta')
			self.metaPar = self.metaComp.par
		elif _isCompMeta(o):
			self.comp = o.par.Hostop.eval()
			# noinspection PyTypeChecker
			self.metaComp = o
			self.metaPar = self.metaComp.par
		else:
			self.comp = None
			self.metaComp = None
			self.metaPar = None

	def __bool__(self):
		return bool(self.comp)

	@property
	def opVersion(self):
		return str(self.metaPar.Opversion)

	@opVersion.setter
	def opVersion(self, val):
		self.metaPar.Opversion = val if val is not None else ''

	@property
	def opType(self):
		return str(self.metaPar.Optype)

	@opType.setter
	def opType(self, val):
		self.metaPar.Optype = val or ''

	@property
	def opStatus(self):
		return str(self.metaPar.Opstatus)

	@opStatus.setter
	def opStatus(self, val):
		self.metaPar.Opstatus = val or 'unset'

	@property
	def opTypeShortName(self):
		"""
		Short form of the name of the COMP type (not the COMP instance).
		"""
		t = self.opType
		return t and t.rsplit('.', 1)[-1]

	@property
	def toxFile(self) -> 'Optional[str]':
		return self.comp.par.externaltox.eval() or None

	@property
	def helpDat(self) -> 'Optional[DAT]':
		dat = op(self.metaPar.Helpdat) or self.comp.op('help')
		if dat and dat.isDAT:
			return dat

	@helpDat.setter
	def helpDat(self, val: 'Optional[DAT]'):
		self.metaPar.Helpdat = val or ''

	@property
	def helpUrl(self):
		return str(self.metaPar.Helpurl)

def _isCompMeta(o: 'OP'):
	return bool(o) and o.isCOMP and o.name == 'componentMeta' and o.par['Hostop'] is not None

def _isLibraryMeta(o: 'OP'):
	return bool(o) and o.isCOMP and o.name == 'libraryMeta' and o.par['Hostop'] is not None

def _isPackageMeta(o: 'OP'):
	return bool(o) and o.isCOMP and o.name == 'packageMeta' and o.par['Hostop'] is not None

class PackageInfo:
	comp: 'Optional[COMP]'
	metaComp: 'Optional[_PackageMetaCompT]'
	metaPar: 'Optional[_PackageMetaParsT]'

	def __init__(self, o: 'Union[OP, str, Cell, Par]'):
		o = op(o)
		if not o or not o.isCOMP:
			return
		if _isPackageMeta(o.op('packageMeta')):
			self.comp = o
			# noinspection PyTypeChecker
			self.metaComp = o.op('packageMeta')
			self.metaPar = self.metaComp.par
		elif _isPackageMeta(o):
			self.comp = o.par.Hostop.eval()
			# noinspection PyTypeChecker
			self.metaComp = o
			self.metaPar = self.metaComp.par
		else:
			self.comp = None
			self.metaComp = None
			self.metaPar = None

	def __bool__(self):
		return bool(self.comp)

	@property
	def packageId(self):
		return str(self.metaPar.Packageid)

	@packageId.setter
	def packageId(self, val: str):
		self.metaPar.Packageid = val

class LibraryInfo:
	comp: 'Optional[COMP]'
	metaComp: 'Optional[_LibraryMetaCompT]'
	metaPar: 'Optional[_LibraryMetaParsT]'

	def __init__(self, o: 'Union[OP, str, Cell, Par]'):
		o = op(o)
		if not o or not o.isCOMP:
			return
		if _isLibraryMeta(o.op('libraryMeta')):
			self.comp = o
			# noinspection PyTypeChecker
			self.metaComp = o.op('libraryMeta')
			self.metaPar = self.metaComp.par
		elif _isLibraryMeta(o):
			self.comp = o.par.Hostop.eval()
			# noinspection PyTypeChecker
			self.metaComp = o
			self.metaPar = self.metaComp.par
		else:
			self.comp = None
			self.metaComp = None
			self.metaPar = None

	def __bool__(self):
		return bool(self.comp)

	@property
	def libraryName(self):
		return str(self.metaPar.Libraryname)

class LibraryContext:
	metaComp: 'Optional[_LibraryMetaCompT]'
	metaPar: 'Optional[_LibraryMetaParsT]'
	libraryRoot: 'Optional[COMP]'
	libraryInfo: 'LibraryInfo'
	callbacks: 'Optional[CallbacksExt]'

	def __init__(
			self,
			metaComp: 'COMP',
			callbacks: 'Optional[CallbacksExt]' = None,
	):
		# noinspection PyTypeChecker
		metaComp = op(metaComp)  # type: _LibraryMetaCompT
		if not metaComp or not metaComp.isCOMP:
			return
		if metaComp.name != 'libraryMeta' or metaComp.par['Hostop'] is None:
			return
		self.libraryRoot = metaComp.par.Hostop.eval()
		self.libraryInfo = LibraryInfo(self.libraryRoot)
		self.metaComp = self.libraryInfo.metaComp
		self.metaPar = self.libraryInfo.metaPar
		self.callbacks = callbacks

	@property
	def valid(self):
		return bool(self.libraryInfo)

	@property
	def packageRoot(self) -> 'Optional[COMP]':
		if not self:
			return None
		return self.metaPar.Packageroot.eval() or self.libraryRoot

	@property
	def componentTags(self) -> 'List[str]':
		return tdu.split(self.metaPar.Componenttags)

	@property
	def packageTags(self) -> 'List[str]':
		return tdu.split(self.metaPar.Packagetags)

	@property
	def libraryName(self):
		return self.libraryInfo.libraryName

	@property
	def libraryVersion(self):
		return str(self.metaPar.Libraryversion)

	def resolvePath(self, path: str) -> 'Optional[COMP]':
		if not self or not path:
			return None
		if path.startswith(self.packageRoot.path + '/'):
			return op(path)
		origRootPath = '/' + self.libraryName + '/'
		if path.startswith(origRootPath):
			return self.libraryRoot.op(path.replace(origRootPath, ''))
		if path.startswith('/'):
			raise ValueError(f'Invalid path outside package root: {path!r}')
		return self.packageRoot.op(path)

	def _doCallback(self, name: str, info: dict):
		if not self.callbacks:
			return
		info = mergeDicts({
			'libraryContext': self,
		}, info)
		self.callbacks.DoCallback(name, info)

	def isPackage(self, comp: 'COMP'):
		if not comp:
			return False
		tags = self.packageTags
		if tags and not any(t in tags for t in comp.tags):
			return False
		return bool(PackageInfo(comp))

	def isComponent(self, comp: 'COMP', checkMaster: bool = False):
		if not comp:
			return False
		if checkMaster:
			master = comp.par.clone.eval()
			if master is not comp:
				return False
		tags = self.componentTags
		if tags and not any(t in tags for t in comp.tags):
			return False
		return bool(CompInfo(comp))

	def getPackage(self, comp: 'COMP', checkParents: bool) -> 'Optional[COMP]':
		if not comp or comp is root:
			return None
		if self.isPackage(comp):
			return comp
		if checkParents:
			return self.getPackage(comp.parent(), checkParents=True)

	def getComponent(self, comp: 'COMP', checkParents: bool) -> 'Optional[COMP]':
		if not comp or comp is root:
			return None
		if self.isComponent(comp):
			return comp
		if checkParents:
			return self.getComponent(comp.parent(), checkParents=True)

	def isWithinPackageRoot(self, comp: 'COMP'):
		if not comp:
			return False
		packageRoot = self.packageRoot
		return comp.path.startswith(packageRoot.path + '/')

	def validateAndGetPackageInfo(self, comp: 'COMP') -> PackageInfo:
		if not self.isPackage(comp):
			raise Exception(f'Invalid package: {comp}')
		return PackageInfo(comp)

	def validateAndGetCompInfo(self, comp: 'COMP') -> CompInfo:
		if not self.isComponent(comp, checkMaster=True):
			raise Exception(f'Invalid component: {comp}')
		return CompInfo(comp)

	def generateOpId(self, comp: 'COMP'):
		path = self.packageRoot.relativePath(comp).strip('./')
		return self.libraryInfo.libraryName + '.' + path.replace('/', '.')

	def packages(self, recursive=False) -> List['COMP']:
		return self.packagesIn(self.packageRoot, recursive)

	def packagesIn(self, packageRoot: 'COMP', recursive=False) -> List['COMP']:
		return self._findComps(packageRoot, self.packageTags, recursive)

	def componentsIn(self, comp: 'COMP', recursive=False) -> List['COMP']:
		return self._findComps(comp, self.componentTags, recursive)

	@staticmethod
	def _findComps(comp: 'COMP', tags: List[str], recursive: bool):
		if not comp or not tags:
			return []
		if recursive:
			return comp.findChildren(
				type=COMP,
				tags=tags,
			)
		else:
			return comp.findChildren(
				type=COMP,
				maxDepth=1,
				tags=tags,
			)

@dataclass
class CompMetaData(DataObjectBase):
	opType: Optional[str] = None
	opVersion: Optional[str] = None
	opStatus: Optional[str] = None
