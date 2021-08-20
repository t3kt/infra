from infraBuild import Builder, BuildContext
from infraCommon import Action
from typing import Callable, Optional, Union

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from _typeAliases import *
	from ..libraryTools.libraryTools import LibraryTools

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
		srcTox = table[name, 'srcToxPath'].val
		return _InfraBuilderBase(
			log=log,
			updateStatus=updateStatus,
			libraryName=name,
			sourceToxPath=srcTox,
		)

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
			self._finalizeLibraryPars()
			self.queueCall(continueAction)
		elif stage == 6:
			self._finalizeLibraryPars()
			self.queueCall(thenRun)

	def _updateLibraryInfo(self, library: COMP):
		pass

	def _finalizeLibraryPars(self):
		pass

	def _exportLibraryTox(self):
		pass

	def processCompImpl(self, comp: 'COMP', thenRun: Callable):
		# TODO: showCustomOnly?
		iop.libraryTools.UpdateComponentMetadata(comp)

		pass
