from infraCommon import navigateTo

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

def onClick(info):
	print(info)
	data = info['rowData']
	path = data['rowObject']['path']
	navigateTo(op(path))
	




