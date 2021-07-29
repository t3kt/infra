from typing import Optional, Union

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from _typeAliases import *

class _MetaParsT(ParCollection):
	Hostop: 'OPParamT'
	Helpurl: 'StrParamT'
	Helpdat: 'OPParamT'
	Toolkitname: 'StrParamT'
	Toolkitversion: 'StrParamT'

class CompMetaParsT(_MetaParsT):
	Optype: 'StrParamT'
	Opversion: 'StrParamT'
	Opstatus: 'StrParamT'

class CategoryMetaParsT(_MetaParsT):
	Categoryid: 'StrParamT'

class ToolkitMetaParsT(_MetaParsT):
	pass

class CompMeta:
	comp: 'Optional[AnyOpT]'
	compMeta: 'Optional[COMP]'
	compMetaPar: 'Optional[CompMetaParsT]'

	def __init__(self, o: 'Union[OP, str, Cell, Par]'):
		o = op(o)
		if not o:
			return
		if _isCompWithMeta(o):
			self.comp = o
			self.compMeta = o.op('compMeta')
			# noinspection PyTypeChecker
			self.compMetaPar = self.compMeta.par
		elif _isCompMeta(o):
			self.comp = o.par.Hostop.eval()
			self.compMeta = o
			# noinspection PyTypeChecker
			self.compMetaPar = self.compMeta.par
		else:
			self.comp = None
			self.compMeta = None
			self.compMetaPar = None

	def __bool__(self):
		return bool(self.comp)

	@property
	def opVersion(self):
		return str(self.compMetaPar.Opversion)

	@opVersion.setter
	def opVersion(self, val):
		self.compMetaPar.Opversion = val if val is not None else ''

	@property
	def opType(self):
		return str(self.compMetaPar.Optype)

	@opType.setter
	def opType(self, val):
		self.compMetaPar.Optype = val or ''

	@property
	def opStatus(self):
		return str(self.compMetaPar.Opstatus)

	@opStatus.setter
	def opStatus(self, val):
		self.compMetaPar.Opstatus = val or 'unset'

	@property
	def isBeta(self):
		return self.opStatus == 'beta'

	@property
	def isAlpha(self):
		return self.opStatus == 'alpha'

	@property
	def isDeprecated(self):
		return self.opStatus == 'deprecated'

	@property
	def opTypeShortName(self):
		"""
		Short form of the name of the COMP type (not the COMP instance).
		"""
		t = self.opType
		return t and t.rsplit('.', 1)[-1]

	@property
	def helpDat(self) -> 'Optional[DAT]':
		dat = op(self.compMetaPar.Helpdat) or self.comp.op('help')
		if dat and dat.isDAT:
			return dat

	@helpDat.setter
	def helpDat(self, val: 'Optional[DAT]'):
		self.compMetaPar.Helpdat = val or ''

	@property
	def helpUrl(self):
		return str(self.compMetaPar.Helpurl)

def _isCompWithMeta(o: 'OP'):
	if not o:
		return False
	compMeta = o.op('compMeta')
	return _isCompMeta(compMeta)

def _isCompMeta(o: 'OP'):
	return bool(o) and o.isCOMP and o.name == 'compMeta' and o.par['Hostop'] is not None
