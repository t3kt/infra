import logging
from typing import Optional, Union

from infraCommon import focusFirstCustomParameterPage, getActiveEditor
from infraMeta import LibraryInfo, CompInfo, CompMetaData, PackageInfo

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from _typeAliases import *

	class _ConfigPar:
		Libraryroot: OPParamT
		Librarymeta: OPParamT
		Packageroot: OPParamT
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

_logger = logging.getLogger(__name__)

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

	def _libraryPackagesRoot(self) -> 'Optional[COMP]':
		config = self._libraryConfig()
		if not config:
			return None
		return config.par.Packageroot.eval() or config.par.Libraryroot.eval()

	def _libraryInfo(self):
		return LibraryInfo(self._libraryRoot())

	def _isMasterComponent(self, comp: 'Optional[COMP]'):
		if not comp or not comp.isCOMP:
			return False
		packageRoot = self._libraryPackagesRoot()
		if not packageRoot or not comp.path.startswith(packageRoot.path + '/'):
			return False
		master = comp.par.clone.eval()
		return bool(master) and master is comp

	def _generateOpId(self, comp: 'COMP'):
		path = self._libraryPackagesRoot().relativePath(comp).strip('./')
		return self._libraryInfo().libraryName + '.' + path.replace('/', '.')

	def _validateAndGetCompInfo(self, comp: 'COMP'):
		info = CompInfo(comp)
		if not info:
			raise Exception(f'Invalid component: {comp}')
		if not self._isMasterComponent(comp):
			raise Exception(f'Component is not master: {comp}')
		return info

	@staticmethod
	def _validateAndGetPackageInfo(comp: 'COMP'):
		info = PackageInfo(comp)
		if not info:
			raise Exception(f'Invalid package: {comp}')
		return info

	def UpdateComponentMetadata(
			self,
			comp: 'COMP',
			incrementVersion=False,
			**kwargs):
		info = self._validateAndGetCompInfo(comp)
		currentOpType = info.opType
		newOpType = self._generateOpId(comp)
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
		self._updateMetaLibraryProperties(info)
		self.DoCallback('onUpdateComponentMetadata', {
			'libraryTools': self,
			'comp': comp,
			'params': kwargs,
		})

	def _updateMetaLibraryProperties(self, info: Union[CompInfo, PackageInfo]):
		libraryInfo = self._libraryInfo()
		info.metaPar.Libraryname = libraryInfo.metaPar.Libraryname
		info.metaPar.Libraryversion = libraryInfo.metaPar.Libraryversion
		info.metaPar.Libraryname.readOnly = True
		info.metaPar.Libraryversion.readOnly = True

	def SaveComponent(
			self,
			comp: 'COMP',
			incrementVersion=False,
			**kwargs):
		self.UpdateComponentMetadata(comp, incrementVersion, **kwargs)
		info = self._validateAndGetCompInfo(comp)
		self.DoCallback('onSaveComponent', {
			'libraryTools': self,
			'comp': comp,
			'params': kwargs,
		})
		# TODO: Docs
		focusFirstCustomParameterPage(comp)
		tox = info.toxFile
		comp.save(tox)

		metaSuffix = self._libraryConfig().par.Metafilesuffix.eval()
		if metaSuffix:
			metaFile = tox.replace('.tox', metaSuffix)
			metaData = self._extractCompMetaData(comp)
			with open(metaFile, 'w') as f:
				f.write(metaData.toJson(minify=False))
		msg = f'Saved TOX {tox} (version: {info.opVersion}'
		ui.status = msg
		_logger.info(msg)

	def SavePackage(self, comp: 'COMP', **kwargs):
		self.UpdatePackageMetadata(comp, **kwargs)
		info = self._validateAndGetPackageInfo(comp)
		self.DoCallback('onSavePackage', {
			'libraryTools': self,
			'comp': comp,
			'params': kwargs,
		})
		# TODO: Docs
		tox = comp.par.externaltox.eval()
		comp.save(tox)
		msg = f'Saved Package {info.packageId} to {tox}'
		ui.status = msg
		_logger.info(msg)

	@staticmethod
	def _extractCompMetaData(comp: 'COMP'):
		info = CompInfo(comp)
		return CompMetaData(
			opType=info.opType,
			opVersion=info.opVersion,
			opStatus=info.opStatus,
		)

	def UpdatePackageMetadata(self, comp: 'COMP', **kwargs):
		info = self._validateAndGetPackageInfo(comp)
		info.packageId = self._generateOpId(comp)
		info.metaPar.Hostop.readOnly = True
		info.metaPar.Packageid.readOnly = True
		self._updateMetaLibraryProperties(info)
		self.DoCallback('onUpdatePackageMetadata', {
			'libraryTools': self,
			'comp': comp,
			'params': kwargs,
		})

	def Createcallbacks(self, _=None):
		par = self.ownerComp.par.Callbackdat
		if par.eval():
			return
		ui.undo.startBlock('Create library tools callbacks')
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

	def _getPrimaryCurrentComponent(self):
		for o in self._getCurrentComponents(primaryOnly=True, masterOnly=True):
			return o

	def _getCurrentComponents(
			self,
			primaryOnly=False,
			masterOnly=False,
	):
		pane = getActiveEditor()
		comp = pane.owner if pane else None
		if not comp:
			return []
		if not self._couldBeLibrarySubComp(comp):
			return []
		c = self._getComponent(comp, checkParents=True)
		if not c:
			try:
				c = self._getComponent(comp.currentChild, checkParents=True)
			except:
				pass
		if masterOnly and not self._isComponent(c):
			c = None
		if c and primaryOnly:
			return [c]
		cs = [c] if c else []
		for child in comp.selectedChildren:
			c = self._getComponent(child, checkParents=False)
			if not c or not self._couldBeLibrarySubComp(c):
				continue
			if masterOnly and not self._isMasterComponent(c):
				continue
			if c and c not in cs:
				cs.append(c)
		return cs

	def _couldBeLibrarySubComp(self, comp: 'COMP'):
		if not comp or not self._libraryPackagesRoot():
			return False
		if comp.path.startswith(self.ownerComp.path + '/'):
			return False
		return comp.path.startswith(self._libraryPackagesRoot().path + '/')

	def _getCurrentPackage(self):
		pane = getActiveEditor()
		comp = pane.owner if pane else None
		if not comp or not self._couldBeLibrarySubComp(comp):
			return None
		return self._getPackage(comp, checkParents=True)

	def _isComponent(self, comp: 'COMP'):
		if not comp:
			return False
		tags = tdu.split(self._libraryConfig().par.Componenttags)
		if tags:
			return any(tag in tags for tag in comp.tags)
		return bool(CompInfo(comp))

	def _isPackage(self, comp: 'COMP'):
		if not comp:
			return
		tags = tdu.split(self._libraryConfig().par.Packagetags)
		if tags:
			return any(tag in tags for tag in comp.tags)
		return bool(PackageInfo(comp))

	def _getComponent(self, comp: 'COMP', checkParents: bool):
		if not comp or comp is root:
			return None
		if self._isComponent(comp):
			return comp
		if checkParents:
			return self._getComponent(comp.parent(), checkParents=True)

	def _getPackage(self, comp: 'COMP', checkParents: bool):
		if not comp or comp is root:
			return None
		if self._isPackage(comp):
			return comp
		if checkParents:
			return self._getPackage(comp.parent(), checkParents=True)

	def buildCurrentComponentTable(self, dat: 'scriptDAT'):
		dat.clear()
		dat.appendRow([
			'path',
			'shortTypeName',
			'opType',
			'opVersion',
			'opStatus',
		])
		comps = self._getCurrentComponents(primaryOnly=False, masterOnly=True)
		for c in comps:
			info = CompInfo(c)
			if not info:
				continue
			dat.appendRow([
				c.path,
				info.opTypeShortName,
				info.opType,
				info.opVersion,
				info.opStatus,
			])

	def buildCurrentPackageTable(self, dat: 'scriptDAT'):
		dat.clear()
		dat.appendRow([
			'path',
			'packageId',
		])
		package = self._getCurrentPackage()
		if package:
			info = PackageInfo(package)
			if info:
				dat.appendRow([
					package.path,
					info.packageId,
				])

	def SaveCurrentComponent(self, incrementVersion=False, **kwargs):
		comp = self._getPrimaryCurrentComponent()
		self.SaveComponent(comp, incrementVersion, **kwargs)

	def SaveCurrentPackage(self, **kwargs):
		comp = self._getCurrentPackage()
		self.SavePackage(comp, **kwargs)

