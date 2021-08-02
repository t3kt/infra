from infraMeta import LibraryInfo, CompInfo

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from _typeAliases import *

	class _ConfigPar:
		Libraryroot: OPParamT
		Librarymeta: OPParamT
		Packagetags: StrParamT
		Componenttags: StrParamT
		Metafilesuffix: StrParamT
	class _ConfigComp(COMP):
		par: _ConfigPar

	class _ToolsPar:
		Libraryconfig: OPParamT
		Callbackdat: OPParamT
	class _ToolsComp(COMP):
		par: _ToolsPar

from TDCallbacksExt import CallbacksExt

class LibraryTools(CallbacksExt):
	def __init__(self, ownerComp: 'COMP'):
		super().__init__(ownerComp)
		# noinspection PyTypeChecker
		self.ownerComp = ownerComp  # type: _ToolsComp

	def _libraryConfig(self) -> 'Optional[_ConfigComp]':
		return self.ownerComp.par.Libraryconfig.eval()

	def _libraryRoot(self) -> 'Optional[COMP]':
		config = self._libraryConfig()
		return config and config.par.Libraryroot.eval()

	def _libraryInfo(self):
		return LibraryInfo(self._libraryRoot())

	def _isMasterComponent(self, comp: 'Optional[COMP]'):
		if not comp or not comp.isCOMP:
			return False
		library = self._libraryRoot()
		if not library or not comp.path.startswith(library.path + '/'):
			return False
		master = comp.par.clone.eval()
		return bool(master) and master is comp

	def _generateOpType(self, compInfo: CompInfo):
		path = self._libraryRoot().relativePath(compInfo.comp).strip('./')
		return self._libraryInfo().libraryName + '.' + path.replace('/', '.')

	def _validateAndGetCompInfo(self, comp: 'COMP'):
		info = CompInfo(comp)
		if not info:
			raise Exception(f'Invalid component: {comp}')
		if not self._isMasterComponent(comp):
			raise Exception(f'Component is not master: {comp}')
		return info

	def UpdateComponentMetadata(
			self,
			comp: 'COMP',
			incrementVersion=False,
			**kwargs):
		info = self._validateAndGetCompInfo(comp)
		currentOpType = info.opType
		newOpType = self._generateOpType(info)
		currentOpVersion = info.opVersion
		info.opType = newOpType
		if not currentOpVersion or not currentOpType or currentOpType != newOpType:
			versionVal = 0
		else:
			versionVal = currentOpVersion
			if incrementVersion:
				versionVal = int(versionVal + 1)
		info.metaPar.Hostop.readOnly = True
		info.opVersion = versionVal
		info.metaPar.Optype.readOnly = True
		info.metaPar.Opversion.readOnly = True
		libraryInfo = self._libraryInfo()
		info.metaPar.Libraryname = libraryInfo.metaPar.Libraryname
		info.metaPar.Libraryversion = libraryInfo.metaPar.Libraryversion
		info.metaPar.Libraryname.readOnly = True
		info.metaPar.Libraryversion.readOnly = True
		self.DoCallback('onUpdateComponentMetadata', {
			'libraryTools': self,
			'comp': comp,
			'compInfo': info,
			'params': kwargs,
		})

