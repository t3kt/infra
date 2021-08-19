from infraBuild import Builder, BuildContext
from infraCommon import Action
from typing import Callable, Optional

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class InfraBuilder:
	def __init__(self, ownerComp: 'COMP'):
		self.ownerComp = ownerComp

	def createBuilder(self, info: dict):
		buildManager = info['buildManager']
		log = info['log']
		updateState = info['updateStatus']
		pass

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

	def runBuildStage(self, stage: int, thenRun: Optional[Callable] = None):
		library = self.getLibraryRoot()
		if stage == 0:
			self.context.detachAllFileSyncDats(library)
		elif stage == 1:
			# TODO: clear old docs?
			self._updateLibraryInfo(library)
		elif stage == 2:
			# TODO: update library image?
			pass
		self.queueCall(Action(self.runBuildStage, [stage + 1, thenRun]))

	def _updateLibraryInfo(self, library: COMP):
		pass
