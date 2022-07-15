import logging
from typing import Union

from infraCommon import focusFirstCustomParameterPage, getActiveEditor
from infraMeta import CompInfo, CompMetaData, PackageInfo, LibraryContext

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from _typeAliases import *

	class _ToolsPar:
		Libraryroot: OPParamT
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

	def GetLibraryContext(self):
		return LibraryContext(self.ownerComp.par.Libraryroot.eval(), callbacks=self)

	def UpdateComponentMetadata(
			self,
			comp: 'COMP',
			incrementVersion=False,
			**kwargs):
		context = self.GetLibraryContext()
		info = context.validateAndGetCompInfo(comp)
		currentOpType = info.opType
		newOpType = context.generateOpId(comp)
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
		packageInfo = PackageInfo(comp.parent())
		if packageInfo:
			info.metaPar.Packagename = packageInfo.packageName
			info.metaPar.Packageid = packageInfo.packageId
		self._updateMetaLibraryProperties(info)
		self.DoCallback('onUpdateComponentMetadata', {
			'libraryTools': self,
			'comp': comp,
			'params': kwargs,
		})

	def _updateMetaLibraryProperties(self, info: Union[CompInfo, PackageInfo]):
		context = self.GetLibraryContext()
		info.metaPar.Libraryname = context.libraryName
		info.metaPar.Libraryversion = context.libraryVersion
		info.metaPar.Libraryname.readOnly = True
		info.metaPar.Libraryversion.readOnly = True

	def SaveComponent(
			self,
			comp: 'COMP',
			incrementVersion=False,
			**kwargs):
		context = self.GetLibraryContext()
		self.UpdateComponentMetadata(comp, incrementVersion, **kwargs)
		info = context.validateAndGetCompInfo(comp)
		self.DoCallback('onSaveComponent', {
			'libraryTools': self,
			'comp': comp,
			'params': kwargs,
		})
		# TODO: Docs
		focusFirstCustomParameterPage(comp)
		tox = info.toxFile
		comp.save(tox)

		metaSuffix = context.metaPar.Metafilesuffix.eval()
		if metaSuffix:
			metaFile = tox.replace('.tox', metaSuffix)
			metaData = self._extractCompMetaData(comp)
			with open(metaFile, 'w') as f:
				f.write(metaData.toJson(minify=False))
		msg = f'Saved TOX {tox} (version: {info.opVersion})'
		ui.status = msg
		_logger.info(msg)

	def SavePackage(self, comp: 'COMP', **kwargs):
		self.UpdatePackageMetadata(comp, **kwargs)
		info = self.GetLibraryContext().validateAndGetPackageInfo(comp)
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
		context = self.GetLibraryContext()
		info = context.validateAndGetPackageInfo(comp)
		info.packageId = context.generateOpId(comp)
		info.packageName = info.packageId.rsplit('.', maxsplit=1)[1]
		info.metaPar.Hostop.readOnly = True
		info.metaPar.Packageid.readOnly = True
		info.metaPar.Packagename.readOnly = True
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
		context = self.GetLibraryContext()
		c = context.getComponent(comp, checkParents=True)
		if not c:
			try:
				c = context.getComponent(comp.currentChild, checkParents=True)
			except:
				pass
		if masterOnly and not context.isComponent(c):
			c = None
		if c and primaryOnly:
			return [c]
		cs = [c] if c else []
		for child in comp.selectedChildren:
			c = context.getComponent(child, checkParents=False)
			if not c or not self._couldBeLibrarySubComp(c):
				continue
			if masterOnly and not context.isComponent(c, checkMaster=True):
				continue
			if c and c not in cs:
				cs.append(c)
		return cs

	def _couldBeLibrarySubComp(self, comp: 'COMP'):
		if not comp or not self.GetLibraryContext().isWithinPackageRoot(comp):
			return False
		if comp.path.startswith(self.ownerComp.path + '/'):
			return False
		return True

	def _getCurrentPackage(self):
		pane = getActiveEditor()
		comp = pane.owner if pane else None
		if not comp or not self._couldBeLibrarySubComp(comp):
			return None
		return self.GetLibraryContext().getPackage(comp, checkParents=True)

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
