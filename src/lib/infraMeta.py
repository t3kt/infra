from typing import Optional, Union

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from _typeAliases import *

	class _MetaParsT:
		Hostop: 'OPParamT'
		Helpurl: 'StrParamT'
		Helpdat: 'OPParamT'
		Toolkitname: 'StrParamT'
		Toolkitversion: 'StrParamT'

	class _CompMetaParsT(_MetaParsT):
		Optype: 'StrParamT'
		Opversion: 'StrParamT'
		Opstatus: 'StrParamT'

	class _CompMetaCompT(COMP):
		par: _CompMetaParsT

	class _CategoryMetaParsT(_MetaParsT):
		Categoryid: 'StrParamT'

	class _CategoryMetaCompT(COMP):
		par: _CategoryMetaParsT

	class _ToolkitMetaParsT(_MetaParsT):
		pass

	class _ToolkitMetaCompT(COMP):
		par: _ToolkitMetaParsT

class CompMeta:
	comp: 'Optional[AnyOpT]'
	metaComp: 'Optional[_CompMetaCompT]'
	metaPar: 'Optional[_CompMetaParsT]'

	def __init__(self, o: 'Union[OP, str, Cell, Par]'):
		o = op(o)
		if not o or not o.isCOMP:
			return
		if _isCompMeta(o.op('compMeta')):
			self.comp = o
			# noinspection PyTypeChecker
			self.metaComp = o.op('compMeta')
			self.metaPar = self.metaComp.par
		elif _isCompMeta(o):
			self.comp = o.par.Hostop.eval()
			# noinspection PyTypeChecker
			self.metaComp = o
			self.metaPar = self.metaComp.par
		else:
			self.comp = None
			self.metaComp = None
			self.metaPar = None

	def __bool__(self):
		return bool(self.comp)

	@property
	def opVersion(self):
		return str(self.metaPar.Opversion)

	@opVersion.setter
	def opVersion(self, val):
		self.metaPar.Opversion = val if val is not None else ''

	@property
	def opType(self):
		return str(self.metaPar.Optype)

	@opType.setter
	def opType(self, val):
		self.metaPar.Optype = val or ''

	@property
	def opStatus(self):
		return str(self.metaPar.Opstatus)

	@opStatus.setter
	def opStatus(self, val):
		self.metaPar.Opstatus = val or 'unset'

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
	def toxFile(self) -> 'Optional[str]':
		return self.comp.par.externaltox.eval() or None

	@property
	def helpDat(self) -> 'Optional[DAT]':
		dat = op(self.metaPar.Helpdat) or self.comp.op('help')
		if dat and dat.isDAT:
			return dat

	@helpDat.setter
	def helpDat(self, val: 'Optional[DAT]'):
		self.metaPar.Helpdat = val or ''

	@property
	def helpUrl(self):
		return str(self.metaPar.Helpurl)

def _isCompMeta(o: 'OP'):
	return bool(o) and o.isCOMP and o.name == 'compMeta' and o.par['Hostop'] is not None

def _isToolkitMeta(o: 'OP'):
	return bool(o) and o.isCOMP and o.name == 'toolkitMeta' and o.par['Hostop'] is not None

class CategoryMeta:
	pass

class ToolkitMeta:
	comp: 'Optional[COMP]'
	metaComp: 'Optional[_ToolkitMetaCompT]'
	metaPar: 'Optional[_ToolkitMetaParsT]'

	def __init__(self, o: 'Union[OP, str, Cell, Par]'):
		o = op(o)
		if not o or not o.isCOMP:
			return
		if _isToolkitMeta(o.op('toolkitMeta')):
			self.comp = o
			# noinspection PyTypeChecker
			self.metaComp = o.op('toolkitMeta')
			self.metaPar = self.metaComp.par
		elif _isToolkitMeta(o):
			self.comp = o.par.Hostop.eval()
			# noinspection PyTypeChecker
			self.metaComp = o
			self.metaPar = self.metaComp.par
		else:
			self.comp = None
			self.metaComp = None
			self.metaPar = None

	@property
	def toolkitName(self):
		return self.metaPar.Toolkitname.eval()
