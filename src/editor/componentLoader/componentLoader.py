from pathlib import Path
from typing import Optional, Type, Union

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

	def LoadComponent(self, tox: 'Union[str, Path]', name: str = None) -> 'COMP':
		self.UnloadComponent()
		convertedPath = _convertPath(tox)
		comp = self.ownerComp.loadTox(convertedPath)
		if not name:
			path = Path(tox)
			name = path.stem
		comp.name = name
		comp.par.externaltox = convertedPath
		return comp

	def CreateNewComponent(
			self, tox: 'Union[str, Path]', name: str = None,
			template: 'Optional[COMP]' = None,
			compType: 'Optional[Type[COMP]]' = None,
			autoSave=True) -> 'COMP':
		self.UnloadComponent()
		if not name:
			path = Path(tox)
			name = path.stem
		if template:
			comp = self.ownerComp.copy(template, name=name, includeDocked=False)
		else:
			comp = self.ownerComp.create(compType or baseCOMP, name=name)
		comp.name = name
		convertedPath = _convertPath(tox)
		comp.par.externaltox = convertedPath
		if autoSave:
			comp.save(convertedPath, createFolders=True)
		return comp

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

def _convertPath(path: 'Union[str, Path]'):
	if isinstance(path, Path):
		return path.as_posix()
	return path
