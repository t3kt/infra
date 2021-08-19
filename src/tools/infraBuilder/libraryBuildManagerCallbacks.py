# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from .infraBuilder import InfraBuilder
	ext.infraBuilder = InfraBuilder(COMP())

def onCreateBuilder(info: dict):
	return ext.infraBuilder.createBuilder(info)
