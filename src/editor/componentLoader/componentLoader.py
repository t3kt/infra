from pathlib import Path
from typing import Optional

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class ComponentLoader:
	def __init__(self, ownerComp: 'COMP'):
		self.ownerComp = ownerComp

	@property
	def Component(self) -> 'Optional[COMP]':
		for o in self.ownerComp.children:
			if o.isCOMP:
				return o

	@property
	def ComponentTox(self) -> 'Optional[str]':
		comp = self.Component
		return comp and comp.par.externaltox.eval()

	@property
	def ComponentName(self) -> 'Optional[str]':
		comp = self.Component
		return comp and comp.name

	def LoadComponent(self, tox: str, name: str = None):
		self.UnloadComponent()
		comp = self.ownerComp.loadTox(tox)
		if not name:
			path = Path(tox)
			name = path.stem
		comp.name = name

	def UnloadComponent(self):
		for o in self.ownerComp.children:
			if not o.isCOMP or not o.valid:
				continue
			# noinspection PyBroadException
			try:
				o.destroy()
			except:
				pass

	def Unloadcomponent(self, _=None):
		self.UnloadComponent()
