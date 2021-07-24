from typing import List, Callable

import infraCommon
import infraTools

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class NetworkToolsPanel:
	def __init__(self, ownerComp: 'COMP'):
		self.ownerComp = ownerComp

	def setFileSyncOnSelected(self, state: bool):
		self._applyTagToSelected(infraTools.InfraTags.fileSync, state)

	def setTagOnSelectedBuildLock(self, state: bool):
		self._applyTagToSelected(infraTools.InfraTags.buildLock, state)

	def setTagOnSelectedBuildExclude(self, state: bool):
		self._applyTagToSelected(infraTools.InfraTags.buildExclude, state)

	def _applyTagToSelected(self, tag: 'infraTools.Tag', state: bool):
		self._forEachSelected(lambda o: tag.apply(o, state))

	def setShowCustomOnlyOnSelected(self, state: bool):
		def _action(o: 'COMP'):
			o.showCustomOnly = state
		self._forEachSelected(_action)

	@staticmethod
	def getActiveEditor():
		return infraCommon.getActiveEditor()

	def getSelectedOps(self) -> 'List[AnyOpT]':
		editor = self.getActiveEditor()
		if not editor:
			return []
		return editor.owner.selectedChildren

	def _forEachSelected(self, action: Callable):
		for o in self.getSelectedOps():
			action(o)
