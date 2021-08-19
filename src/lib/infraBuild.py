from abc import ABC, abstractmethod
from infraCommon import detachTox, queueCall, Action
from infraTools import InfraTags
from typing import Callable, List, Optional

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

def _noLog(msg: str): pass

class Builder(ABC):
	def __init__(
			self,
			log: Optional[Callable[[str], None]],
			updateStatus: Callable[[str], None],
			libraryName: str,
			sourceToxPath: str,
			buildDirPath: str,
			paneName: Optional[str] = None,
	):
		self._log = log or _noLog
		self._updateStatus = updateStatus
		self.paneName = paneName or 'infraBuildPane'
		self.context = None  # type: Optional[BuildContext]
		self.libraryName = libraryName
		self.sourceToxPath = sourceToxPath
		self.buildDirPath = buildDirPath

	def openLibraryNetwork(self):
		comp = self.getLibraryRoot()
		if not self.context:
			self.initialize()
		self.context.openNetworkPane(comp)

	def initialize(self):
		self.log('Initializing builder')
		self.context = self.createBuildContext()
		self.log('Build context initialized')

	def createBuildContext(self) -> Optional['BuildContext']:
		return BuildContext(self)

	def getLibraryRoot(self) -> Optional[COMP]:
		return getattr(op, self.libraryName)

	def unloadLibrary(self):
		comp = self.getLibraryRoot()
		if not comp:
			return
		self.log('Unloading library')
		# noinspection PyBroadException
		try:
			comp.destroy()
		except:
			pass

	def loadLibrary(self, thenRun: Optional[Callable] = None):
		self.unloadLibrary()
		self.log(f'Loading library tox {self.sourceToxPath}...')
		def _load():
			comp = root.loadTox(self.sourceToxPath)
			self.log(f'Loaded library tox: {comp}')
			if thenRun:
				self.queueCall(thenRun)
		self.queueCall(_load)

	def startBuild(self, thenRun: Optional[Callable] = None):
		self.log('Starting build')
		self.initialize()

		def _afterLoad():
			self.context.openNetworkPane(self.getLibraryRoot())
			self.queueCall(self.runBuildStage, 0, thenRun)

		self.loadLibrary(_afterLoad)

	@abstractmethod
	def runBuildStage(self, stage: int, thenRun: Optional[Callable] = None):
		pass

	def log(self, message: str):
		self._log(message)

	@staticmethod
	def queueCall(action: Callable, *args, delayFrames=5):
		queueCall(action, *args, delayFrames=delayFrames)

class BuildContext:
	def __init__(
			self,
			builder: Builder,
	):
		self.builder = builder
		self.log = builder.log or _noLog
		self._paneName = builder.paneName or 'infraBuildPane'
		self._pane: Optional[NetworkEditor] = None

	def _findExistingPane(self):
		for pane in ui.panes:
			if pane.name == self._paneName:
				self._pane = pane
				return

	def openNetworkPane(self, comp: 'COMP'):
		self._findExistingPane()
		if not self._pane:
			self._pane = ui.panes.createFloating(type=PaneType.NETWORKEDITOR, name=self._paneName)
		self.moveNetworkPane(comp)

	def closeNetworkPane(self):
		if self._pane:
			self._pane.close()
			self._pane = None

	def moveNetworkPane(self, comp: 'COMP'):
		if self._pane:
			self._pane.owner = comp

	def focusInNetworkPane(self, o: 'OP'):
		if o and self._pane:
			self._pane.owner = o.parent()
			self._pane.home(zoom=True, op=o)
			o.current = True

	def detachTox(self, comp: 'COMP'):
		if not comp or comp.par['externaltox'] is None:
			return
		if not comp.par.externaltox and comp.par.externaltox.mode == ParMode.CONSTANT:
			return
		self.log(f'Detaching tox from {comp}')
		detachTox(comp)

	def reclone(self, comp: 'COMP'):
		if not comp or not comp.par['enablecloningpulse'] or not comp.par['clone']:
			return
		self.log(f'Recloning {comp}')
		comp.par.enablecloningpulse.pulse()

	def disableCloning(self, comp: 'COMP'):
		if not comp or comp.par['enablecloning'] is None:
			return
		self.log(f'Disabling cloning on {comp}')
		comp.par.enablecloning.expr = ''
		comp.par.enablecloning = False

	def detachDat(self, dat: 'DAT', reloadFirst=False):
		if not dat or dat.par['file'] is None:
			return
		if not dat.par.file and dat.par.file.mode == ParMode.CONSTANT:
			return
		self.log(f'Detaching DAT {dat}')
		for par in dat.pars('syncfile', 'loadonstart', 'loadonstartpulse', 'write', 'writepulse'):
			par.expr = ''
			par.val = False
		if reloadFirst and dat.par['loadonstartpulse'] is not None:
			dat.par.loadonstartpulse.pulse()
		dat.par.file.expr = ''
		dat.par.file.val = ''

	def detachAllFileSyncDats(self, scope: 'COMP'):
		if not scope:
			return
		self.log(f'Detaching file sync dats in {scope}...')
		for dat in scope.findChildren(tags=[InfraTags.fileSync.name], type=DAT):
			self.detachDat(dat, reloadFirst=True)

	def resetCustomPars(self, o: 'OP'):
		if not o:
			return
		self.log(f'Resetting pars on {o}')
		for par in o.customPars:
			if par.readOnly or not par.enable:
				continue
			par.val = par.default

	# TODO: lockPars()


	def reloadTox(self, comp: 'COMP'):
		if not comp or not comp.par['reinitnet'] or not comp.par['externaltox']:
			return
		self.log(f'Reloading {comp.par.externaltox} for {comp}')
		comp.par.reinitnet.pulse()

	def safeDestroyOp(self, o: 'OP'):
		if not o or not o.valid:
			return
		self.log(f'Removing {o}')
		try:
			o.destroy()
		except Exception as e:
			self.log(f'Ignoring error removing {o}: {e}')

	def safeDestroyOps(self, os: 'List[OP]'):
		for o in os:
			self.safeDestroyOp(o)

	def lockOps(self, os: 'List[OP]'):
		for o in os:
			if o.lock:
				continue
			self.log(f'Locking {o}')
			o.lock = True

	def lockBuildLockOps(self, comp: 'COMP'):
		self.log(f'Locking build locked ops in {comp}')
		toLock = comp.findChildren(tags=[InfraTags.buildLock.name])
		self.lockOps(toLock)

	def removeBuildExcludeOps(self, comp: 'COMP'):
		self.log(f'Removing build excluded ops from {comp}')
		toRemove = list(comp.findChildren(tags=[InfraTags.buildExclude.name]))
		self.safeDestroyOps(toRemove)

	def queueCall(self, action: Callable, *args, delayFrames=5):
		self.builder.queueCall(action, *args, delayFrames=delayFrames)

	def runBuildScript(self, dat: 'DAT', thenRun: Callable):
		self.log(f'Running build script: {dat}')

		def _finish():
			self.log(f'Finished running build script: {dat}')
			self.queueCall(thenRun)

		subContext = BuildTaskContext(self.builder, _finish)
		dat.run(subContext, delayFrames=5)

class BuildTaskContext(BuildContext):
	def __init__(
			self,
			builder: Builder,
			finish: Callable[[], None],
	):
		super().__init__(builder)
		self._finish = finish

	def finishTask(self):
		self._finish()

