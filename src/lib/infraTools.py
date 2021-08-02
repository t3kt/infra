from typing import Callable, Tuple, Union

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class Tag:
	"""
	A tag that can be applied to OPs which tools use to apply various types of behaviors.
	"""
	def __init__(
			self,
			name: str,
			color: Tuple[float, float, float] = None,
			update: Callable[['OP', bool], None] = None):
		"""
		:param name: the tag name
		:param color: Optional RGB color applied to OPs that use the tag.
		:param update: Optional function that applies tag-specific behavior to OPs.
		"""
		self.name = name
		self.color = color
		self.update = update

	def apply(self, o: 'OP', state: bool):
		"""
		Add/remove the tag on an OP, and update the color (if applicable), and apply the update function (if applicable)
		"""
		self.applyTag(o, state)
		self.applyColor(o, state)
		self.applyUpdate(o, state)

	def applyUpdate(self, o: 'OP', state: bool):
		"""
		Apply the tag's update function to an OP, performing tag-specific changes.
		"""
		if o and self.update:
			self.update(o, state)

	def applyTag(self, o: 'OP', state: bool):
		"""
		Add/remove the tag on an OP
		"""
		if not o:
			return
		if state:
			o.tags.add(self.name)
		elif self.name in o.tags:
			o.tags.remove(self.name)

	def applyColor(self, o: 'OP', state: bool):
		"""
		If applicable, set the color of an OP to either the tag's color or the default color.
		"""
		if self.color:
			o.color = self.color if state else _defaultNodeColor

	def __str__(self):
		return self.name

	def isOn(self, o: 'OP'):
		return bool(o) and self.name in o.tags

_defaultNodeColor = 0.545, 0.545, 0.545
_buildExcludeColor = 0.1, 0.1, 0.1
_fileSyncColor = 0.65, 0.5, 1
_buildLockColor = 0, 0.68, 0.543
_alphaColor = 1, 0.55, 0
_betaColor = 1, 0, 0.5
_deprecatedColor = 0.2, 0.2, 0.2

def _updateFileSyncPars(o: 'Union[OP, DAT]', state: bool):
	if o.isDAT:
		filePar = o.par['file']
		if filePar and state:
			o.save(filePar.eval())
		if o.par['defaultreadencoding'] is not None:
			o.par.defaultreadencoding = 'utf8'
		par = o.par['syncfile']
		if par is not None:
			par.expr = ''
			par.val = state
			if not state:
				for par in o.pars('loadonstart', 'loadonstartpulse', 'write', 'writepulse'):
					par.expr = ''
					par.val = False
		else:
			for par in o.pars('loadonstart', 'loadonstartpulse', 'write', 'writepulse'):
				par.expr = ''
				par.val = state
	else:
		# TODO: support for other types of OPs
		raise Exception(f'updateFileSyncPars does not yet support op: {o}')

class InfraTags:
	buildExclude = Tag('buildExclude', _buildExcludeColor)
	"""Indicates that an OP should be removed during the build process."""

	buildLock = Tag('buildLock', _buildLockColor)
	"""Indicates that an OP should be locked during the build process."""

	fileSync = Tag('fileSync', _fileSyncColor, _updateFileSyncPars)
	"""Indicates that a DAT is synced with an external file (when in development mode)."""
