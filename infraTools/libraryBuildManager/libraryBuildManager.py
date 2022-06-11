from datetime import datetime
from infraBuild import Builder
from typing import Optional

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

from TDCallbacksExt import CallbacksExt

class LibraryBuildManager(CallbacksExt):
	def __init__(self, ownerComp: 'COMP'):
		super().__init__(ownerComp)
		self.logTable = ownerComp.op('log')
		self.builder = None  # type: Optional[Builder]

	def startBuild(self):
		self.clearLog()
		self._initializeBuilder()
		def _afterBuild():
			self.log('Build completed!')
			# TODO: update status
			pass
		self.builder.startBuild(_afterBuild)

	def reloadLibrary(self):
		if self.builder or self._initializeBuilder():
			self.builder.loadLibrary()

	def openLibrary(self):
		if self.builder or self._initializeBuilder():
			self.builder.openLibraryNetwork()

	@staticmethod
	def openTextport():
		ui.openTextport()

	def openLog(self):
		dat = self.ownerComp.op('fullLogText')
		dat.openViewer()

	def clearLog(self):
		self.logTable.clear()

	def log(self, message: str):
		print(message)
		self.logTable.appendRow([_timestamp() + ':', message])

	def _updateStatus(self, status: str):
		# TODO: update status...
		pass

	def _initializeBuilder(self):
		self.log('Initializing builder')
		self.buildContext = None
		try:
			result = self.DoCallback('onCreateBuilder', {
				'buildManager': self,
				'log': self.log,
				'updateStatus': self._updateStatus,
			}) or {}
			self.builder = result.get('returnValue')
		except Exception as error:
			self.log(f'Error: {error}')
		if not self.builder:
			self.log('Unable to create builder!')
			return False
		self.log('Builder initialized')
		return True

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


_timestampFormat = '[%H:%M:%S]'
_preciseTimestampFormat = '[%H:%M:%S.%f]'

def _timestamp():
	return datetime.now().strftime(
		# _timestampFormat
		_preciseTimestampFormat
	)