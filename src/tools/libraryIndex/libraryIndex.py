from typing import Dict

from infraMeta import LibraryContext, PackageInfo, CompInfo

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from _typeAliases import *

	class _IndexPar:
		Librarymeta: OPParamT
	class _IndexComp(COMP):
		par: _IndexPar

class LibraryIndex:
	def __init__(self, ownerComp: 'COMP'):
		# noinspection PyTypeChecker
		self.ownerComp = ownerComp  # type: _IndexComp

	def _libraryContext(self):
		return LibraryContext(self.ownerComp.par.Librarymeta.eval())

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
			'relPath',
			'depth',
		])
		context = self._libraryContext()
		for package in context.packages(recursive=True):
			info = PackageInfo(package)
			if not info:
				continue
			relPath = context.packageRoot.relativePath(package).strip('./')
			dat.appendRow([
				info.packageId,
				package.path,
				relPath,
				relPath.count('/'),
			])

	def buildComponentTable(self, dat: 'scriptDAT'):
		dat.clear()
		dat.appendRow([
			'opType',
			'shortName',
			'fullName',
			'path',
			'relPath',
			'packageId',
			'tags',
			'opVersion',
			'opStatus',
		])
		context = self._libraryContext()
		for comp in context.componentsIn(context.packageRoot, recursive=True):
			info = CompInfo(comp)
			if not info:
				continue
			packageInfo = PackageInfo(comp.parent())
			dat.appendRow([
				info.opType,
				info.opTypeShortName,
				context.packageRoot.relativePath(comp).strip('./'),
				comp.path,
				context.libraryRoot.relativePath(comp).strip('./'),
				packageInfo.packageId if packageInfo else '',
				' '.join(sorted(comp.tags)),
				info.opVersion,
				info.opStatus,
			])

