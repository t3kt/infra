# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from infraBuild import BuildTaskContext
	from _stubs import *

context = args[0]  # type: BuildTaskContext

context.log('Processing libraryPalette')
picker = op('libraryOpPicker')
context.detachTox(picker)
context.disableCloning(picker)
context.finishTask()
