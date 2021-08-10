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
		metas = root.findChildren(
			type=baseCOMP,
			path='*/libraryMeta',
		)
		for meta in metas:
			# hard-coded exclusion...
			if meta.path == '/infraMeta/meta/libraryMeta':
				continue
			info = LibraryInfo(meta.par.Hostop)
			if info:
				dat.appendRow([
					info.comp.path,
					info.libraryName,
				])
