import logging
from typing import Optional

from infraCommon import focusFirstCustomParameterPage
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
		self.ownerComp = ownerComp  # type: _ToolsComp

	def _toolkitConfig(self) -> 'Optional[_ConfigComp]':
		return self.ownerComp.par.Toolkitconfig.eval()

	def _toolkitRoot(self) -> 'Optional[COMP]':
		config = self._toolkitConfig()
		return config and config.par.Toolkitroot.eval()

	def _toolkitMeta(self):
		return ToolkitMeta(self._toolkitRoot())

	def isMasterComponent(self, comp: 'Optional[COMP]'):
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
		if not self.isMasterComponent(comp):
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
		meta.opVersion = versionVal
		toolkitMeta = self._toolkitMeta()
		meta.metaPar.Toolkitname = toolkitMeta.metaPar.Toolkitname
		meta.metaPar.Toolkitversion = toolkitMeta.metaPar.Toolkitversion
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
