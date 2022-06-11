from infraBuild import Builder
from infraCommon import Action
from typing import Callable, Optional

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from _typeAliases import *
	from infraTools.libraryTools.libraryTools import LibraryTools

	class _BuilderStatePar:
		Selectedlibrary: StrParamT

	ipar.builderState = _BuilderStatePar()
	# noinspection PyTypeHints
	iop.libraryTools = LibraryTools(COMP())  # type: Union[LibraryTools, COMP]

class InfraBuilder:
	def __init__(self, ownerComp: 'COMP'):
		self.ownerComp = ownerComp

	def createBuilder(self, info: dict):
		buildManager = info['buildManager']
		log = info['log']
		updateStatus = info['updateStatus']

		table = self.ownerComp.op('infraLibraries')
		name = ipar.builderState.Selectedlibrary.eval()
		if not name:
			return
		self.ownerComp.op('libraryTools').par.Libraryroot = '/' + name
		srcTox = table[name, 'sourceToxPath'].val
		return _InfraBuilderBase(
			log=log,
			updateStatus=updateStatus,
			libraryName=name,
			sourceToxPath=srcTox,
		)

	def Openwindow(self, _=None):
		self.ownerComp.op('window').par.winopen.pulse()

class _InfraBuilderBase(Builder):
	def __init__(
			self,
			log: Optional[Callable[[str], None]],
			updateStatus: Callable[[str], None],
			libraryName: str,
			sourceToxPath: str,
	):
		super().__init__(
			log=log,
			updateStatus=updateStatus,
			libraryName=libraryName,
			sourceToxPath=sourceToxPath,
			buildDirPath='build/',
			paneName='infraBuildPane',
		)

	def runBuildStage(self, stage: int, thenRun: Callable):
		continueAction = Action(self.runBuildStage, [stage + 1, thenRun])
		library = self.getLibraryRoot()
		if stage == 0:
			self.context.detachAllFileSyncDats(library)
			self.queueCall(continueAction)
		elif stage == 1:
			# TODO: clear old docs?
			self._updateLibraryInfo(library)
			self.queueCall(continueAction)
		elif stage == 2:
			# TODO: update library image?
			self.processPackages(continueAction)
		elif stage == 3:
			self.context.lockBuildLockOps(library)
			self.queueCall(continueAction)
		elif stage == 4:
			self.context.removeBuildExcludeOps(library)
			self.queueCall(continueAction)
		elif stage == 5:
			self.finalizeLibraryPars()
			self.queueCall(continueAction)
		elif stage == 6:
			self.exportLibraryTox()
			self.context.closeNetworkPane()
			self.queueCall(thenRun)
		else:
			self.queueCall(thenRun)

	def _updateLibraryInfo(self, library: COMP):
		pass

	def processCompImpl(self, comp: 'COMP', thenRun: Callable):
		# TODO: showCustomOnly?
		iop.libraryTools.UpdateComponentMetadata(comp)
		# TODO: update comp params
		self._updateComponentParams(comp)
		self.context.resetCustomPars(comp)
		# TODO: lock buildLock pars

		# TODO: process sub components
		# TODO: update op image
		# TODO: set comp color
		# TODO: process docs

		self.queueCall(thenRun)

	def _updateComponentParams(self, comp: 'COMP'):
		self.log(f'Updating component params {comp}')
		comp.par.enablecloning = False
		comp.par.reloadtoxonstart.expr = ''
		comp.par.reloadtoxonstart.val = False
		comp.par.reloadcustom.expr = ''
		comp.par.reloadcustom.val = False
		comp.par.reloadbuiltin.expr = ''
		comp.par.reloadbuiltin.val = False
