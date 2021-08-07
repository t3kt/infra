from infraMeta import LibraryInfo

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class LibrarySwitcher:
	def __init__(self, ownerComp: 'COMP'):
		self.ownerComp = ownerComp

	@staticmethod
	def buildLibraryTable(
			dat: 'DAT'):
		dat.clear()
		dat.appendRow(['path', 'name'])
		configs = root.findChildren(
			type=baseCOMP,
			path='*/libraryConfig',
		)
		for config in configs:
			# hard-coded exclusion...
			if config.path == '/infraMeta/meta/libraryConfig':
				continue
			info = LibraryInfo(config.par.Libraryroot)
			if info:
				dat.appendRow([
					info.comp.path,
					info.libraryName,
				])
