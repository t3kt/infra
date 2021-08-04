from infraMeta import LibraryContext, PackageInfo

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from _typeAliases import *

	class _IndexPar:
		Libraryconfig: OPParamT
	class _IndexComp(COMP):
		par: _IndexPar

class LibraryIndex:
	def __init__(self, ownerComp: 'COMP'):
		# noinspection PyTypeChecker
		self.ownerComp = ownerComp  # type: _IndexComp

	def _libraryContext(self):
		return LibraryContext(self.ownerComp.par.Libraryconfig.eval())

	def buildLibraryInfoTable(self, dat: 'scriptDAT'):
		dat.clear()
		context = self._libraryContext()
		dat.appendRow(['libraryName', context.libraryName])
		dat.appendRow(['libraryVersion', context.libraryVersion])
		dat.appendRow(['packageRoot', context.packageRoot])

	def buildPackageTable(self, dat: 'scriptDAT'):
		dat.clear()
		dat.appendRow([
			'packageId',
			'path',
		])
		context = self._libraryContext()
		for package in context.packages(recursive=True):
			info = PackageInfo(package)
			if info:
				dat.appendRow([
					info.packageId,
					package.path,
				])

