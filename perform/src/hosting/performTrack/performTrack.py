# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from components.hosting.componentLoader.componentLoader import ComponentLoader
	iop.loader = ComponentLoader(COMP())

class PerformTrack:
	def __init__(self, ownerComp: 'COMP'):
		self.ownerComp = ownerComp

	def promptLoadTox(self):
		tox = ui.chooseFile(
			load=True,
			fileTypes=['tox'],
			title=f'Load scene for {self.ownerComp.par.Header}',
		)
		if tox:
			iop.loader.LoadComponent(tox)

	@staticmethod
	def unloadTox():
		iop.loader.UnloadComponent()

