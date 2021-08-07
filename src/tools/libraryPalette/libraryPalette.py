import logging
from typing import Union, Optional

from infraCommon import getActiveEditor, detachTox, focusFirstCustomParameterPage
from infraMeta import LibraryContext

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from _typeAliases import *
	from ..libraryOpPicker.libraryOpPicker import LibraryOpPicker, PickerCompItem, PickerPackageItem

	iop.picker = LibraryOpPicker(COMP())

	class _PalettePar:
		Libraryindex: OPParamT
		Libraryroot: OPParamT
		Devel: BoolParamT
		Newopcolorr: FloatParamT
		Newopcolorg: FloatParamT
		Newopcolorb: FloatParamT
		Callbackdat: OPParamT
	class _PaletteComp(COMP):
		par: _PalettePar

from TDCallbacksExt import CallbacksExt

_logger = logging.getLogger(__name__)

class LibraryPalette(CallbacksExt):
	def __init__(self, ownerComp: 'COMP'):
		super().__init__(ownerComp)
		# noinspection PyTypeChecker
		self.ownerComp = ownerComp  # type: _PaletteComp

	def _libraryContext(self):
		return LibraryContext(
			configComp=self.ownerComp.par.Libraryindex.eval().par.Libraryconfig.eval(),
			callbacks=self,
		)

	def picker_onPickItem(self, item: 'Union[PickerCompItem, PickerPackageItem]'):
		if not item or not item.isComp:
			return
		template = self._getTemplate(item)
		if not template:
			self._log(f'Unable to find template for path: {item.path}', isError=True)
			return
		pane = getActiveEditor()
		dest = pane and pane.owner  # type: COMP
		if not dest:
			self._log('Unable to find active network editor pane', isError=True)
			return
		newOp = self._createComp(
			template, dest,
			nodeX=pane.x, nodeY=pane.y,
			name=template.name + ('1' if tdu.digits(template.name) is None else ''),
			item=item,
		)
		ui.undo.startBlock(f'Create {item.shortName}')
		ui.undo.addCallback(self._createCompDoHandler, {
			'template': template,
			'dest': dest,
			'nodeX': pane.x,
			'nodeY': pane.y,
			'name': newOp.name,
			'item': item,
		})
		ui.undo.endBlock()
		# TODO: close?

	def _createComp(
			self, template: 'COMP', dest: 'COMP',
			nodeX: float, nodeY: float, name: str,
			item: 'PickerCompItem'):
		newOp = dest.copy(
			template,
			name=name,
		)  # type: COMP
		newOp.nodeCenterX = nodeX
		newOp.nodeCenterY = nodeY
		detachTox(newOp)
		# TODO: opImage?
		enableCloning = newOp.par.enablecloning  # type: Par
		enableCloning.expr = ''
		enableCloning.val = self.ownerComp.par.Devel.eval()
		focusFirstCustomParameterPage(newOp)
		for par in newOp.customPars:
			if par.readOnly or par.isPulse or par.isMomentary or par.isDefault:
				continue
			if par.mode in (ParMode.EXPORT, ParMode.BIND):
				continue
			if par.defaultExpr and par.defaultExpr != par.default:
				par.expr = par.defaultExpr
			else:
				par.val = par.default
		newOp.allowCooking = True
		newOp.color = self.ownerComp.par.Newopcolorr, self.ownerComp.par.Newopcolorg, self.ownerComp.par.Newopcolorb
		self.DoCallback('onCreateComp', {
			'palette': self,
			'newOp': newOp,
			'template': template,
			'item': item,
		})
		return newOp

	def _createCompDoHandler(self, isUndo: bool, info: dict):
		dest = info['dest']  # type: COMP
		name = info['name']
		if isUndo:
			self._log(f'Undoing create OP: {dest.path}/{name}')
			newOp = dest.op(name)
			if newOp and newOp.valid:
				try:
					newOp.destroy()
				except:
					pass
		else:
			self._log(f'Redoing create OP: {dest.path}/{name}')
			self._createComp(
				template=info['template'],
				dest=info['dest'],
				nodeX=info['nodeX'],
				nodeY=info['nodeY'],
				name=name,
				item=info['item'],
			)

	def _getTemplate(self, item: 'PickerCompItem') -> Optional['COMP']:
		if not item or not item.isComp:
			return
		context = self._libraryContext()
		return context.resolvePath(item.path)

	def _log(self, msg: str, isError=False):
		ui.status = msg
		if isError:
			_logger.error(msg)
			self.DoCallback('onError', {'message': msg, 'palette': self})
		else:
			_logger.info(msg)
			self.DoCallback('onMessage', {'message': msg, 'palette': self})

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
