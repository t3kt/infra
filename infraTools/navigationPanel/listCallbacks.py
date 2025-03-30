from infraCommon import navigateTo

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

def onSelectRow(info):
	print(info)
	data = info['rowData']
	path = data['rowObject']['path']
	navigateTo(op(path))
	




