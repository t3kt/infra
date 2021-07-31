import logging
from typing import Optional, Callable

from infraCommon import focusFirstCustomParameterPage, getActiveEditor
from infraMeta import CompMeta, ToolkitMeta

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from _typeAliases import *

	class _ConfigPar:
		Toolkitroot: OPParamT
		Toolkitmeta: OPParamT
		Categorytags: StrParamT
		Componenttags: StrParamT
	class _ConfigComp(COMP):
		par: _ConfigPar

	class _ToolsPar:
		Toolkitconfig: OPParamT
		Callbackdat: OPParamT
	class _ToolsComp(COMP):
		par: _ToolsPar

try:
	# noinspection PyUnresolvedReferences
	CallbacksExt = op.TDModules.op('TDCallbacksExt').module.CallbacksExt
except ImportError:
	from _stubs.TDCallbacksExt import CallbacksExt

_logger = logging.getLogger(__name__)

class ToolkitTools(CallbacksExt):
	def __init__(self, ownerComp: 'COMP'):
		super().__init__(ownerComp)
		# noinspection PyTypeChecker
		self.ownerComp = ownerComp  # type: _ToolsComp

	def _toolkitConfig(self) -> 'Optional[_ConfigComp]':
		return self.ownerComp.par.Toolkitconfig.eval()

	def _toolkitRoot(self) -> 'Optional[COMP]':
		config = self._toolkitConfig()
		return config and config.par.Toolkitroot.eval()

	def _toolkitMeta(self):
		return ToolkitMeta(self._toolkitRoot())

	def _isMasterComponent(self, comp: 'Optional[COMP]'):
		if not comp or not comp.isCOMP:
			return False
		toolkit = self._toolkitRoot()
		if not toolkit or not comp.path.startswith(toolkit.path + '/'):
			return False
		master = comp.par.clone.eval()
		return bool(master) and master is comp

	def _generateOpType(self, meta: CompMeta):
		path = self._toolkitRoot().relativePath(meta.comp).strip('./')
		return self._toolkitMeta().toolkitName + '.' + path.replace('/', '.')

	def _validateAndGetCompMeta(self, comp: 'COMP'):
		meta = CompMeta(comp)
		if not meta:
			raise Exception(f'Invalid component: {comp}')
		if not self._isMasterComponent(comp):
			raise Exception(f'Component is not master: {comp}')
		return meta

	def UpdateComponentMetadata(
			self,
			comp: 'COMP',
			incrementVersion=False,
			**kwargs):
		meta = self._validateAndGetCompMeta(comp)
		currentOpType = meta.opType
		newOpType = self._generateOpType(meta)
		currentOpVersion = meta.opVersion
		meta.opType = newOpType
		if not currentOpVersion or not currentOpType or currentOpType != newOpType:
			versionVal = 0
		else:
			versionVal = currentOpVersion
			if incrementVersion:
				versionVal = int(versionVal + 1)
		meta.metaPar.Hostop.readOnly = True
		meta.opVersion = versionVal
		meta.metaPar.Optype.readOnly = True
		meta.metaPar.Opversion.readOnly = True
		toolkitMeta = self._toolkitMeta()
		meta.metaPar.Toolkitname = toolkitMeta.metaPar.Toolkitname
		meta.metaPar.Toolkitversion = toolkitMeta.metaPar.Toolkitversion
		meta.metaPar.Toolkitname.readOnly = True
		meta.metaPar.Toolkitversion.readOnly = True
		self.DoCallback('onUpdateComponentMetadata', {
			'toolkitTools': self,
			'comp': comp,
			'compMeta': meta,
			'params': kwargs,
		})

	def SaveComponent(
			self,
			comp: 'COMP',
			incrementVersion=False,
			**kwargs):
		meta = self._validateAndGetCompMeta(comp)
		self.UpdateComponentMetadata(comp, incrementVersion, **kwargs)
		self.DoCallback('onSaveComponent', {
			'toolkitTools': self,
			'comp': comp,
			'compMeta': meta,
			'params': kwargs,
		})
		# TODO: Docs
		focusFirstCustomParameterPage(comp)
		tox = meta.toxFile
		comp.save(tox)
		msg = f'Saved TOX {tox} (version: {meta.opVersion}'
		ui.status = msg
		_logger.info(msg)

	def Createcallbacks(self, _=None):
		par = self.ownerComp.par.Callbackdat
		if par.eval():
			return
		ui.undo.startBlock('Create toolkit tools callbacks')
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
		def _shouldExclude(o: 'COMP'):
			return o is self.ownerComp or o.path.startswith(self.ownerComp.path + '/')

		pane = getActiveEditor()
		if not pane:
			return []
		comp = pane.owner
		if not comp:
			return []
		if _shouldExclude(comp):
			return []
		c = self._getComponent(comp) or self._getComponent(comp.currentChild)
		if masterOnly and not self._isComponent(c):
			c = None
		if c and primaryOnly:
			return [c]
		cs = [c] if c else []
		for child in comp.selectedChildren:
			c = self._getComponent(child, checkParents=False)
			if not c or _shouldExclude(c):
				continue
			if masterOnly and not self._isMasterComponent(c):
				continue
			if c and c not in cs:
				cs.append(c)
		return cs

	def _isComponent(self, comp: 'COMP'):
		if not comp:
			return False
		compTags = tdu.split(self._toolkitConfig().par.Componenttags)
		if compTags:
			return any(tag in compTags for tag in comp.tags)
		return bool(CompMeta(comp))

	def _getComponent(self, comp: 'COMP', checkParents=True):
		if not comp or comp is root:
			return None
		if self._isComponent(comp):
			return comp
		if checkParents:
			return self._getComponent(comp.parent(), checkParents=True)

	def buildCurrentComponentsTable(self, dat: 'scriptDAT'):
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
			meta = CompMeta(c)
			dat.appendRow([
				c.path,
				meta.opTypeShortName,
				meta.opType,
				meta.opVersion,
				meta.opStatus,
			])

	def SaveCurrentComponent(self, incrementVersion=False, **kwargs):
		comp = self._getPrimaryCurrentComponent()
		self.SaveComponent(comp, incrementVersion, **kwargs)

