from typing import Callable, Optional, Union

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *


def getActiveEditor() -> 'NetworkEditor':
	pane = ui.panes.current
	if pane and pane.type == PaneType.NETWORKEDITOR:
		return pane
	for pane in ui.panes:
		if pane.type == PaneType.NETWORKEDITOR:
			return pane

def getPaneByName(name: str):
	for pane in ui.panes:
		if pane.name == name:
			return pane

def getEditorPane(name: Optional[str] = None, popup=False):
	if name:
		pane = getPaneByName(name)
	else:
		pane = getActiveEditor()
	if pane:
		if popup:
			return pane.floatingCopy()
		return pane
	else:
		return ui.panes.createFloating(type=PaneType.NETWORKEDITOR, name=name)

def navigateTo(o: 'Union[OP, COMP]', name: Optional[str] = None, popup=False, goInto=True):
	if not o:
		return
	pane = getEditorPane(name, popup)
	if not pane:
		return
	if goInto and o.isCOMP:
		pane.owner = o
	else:
		pane.owner = o.parent()
		o.current = True
		o.selected = True
		pane.homeSelected(zoom=False)

def cleanDict(d):
	if not d:
		return None
	result = {}
	for key, val in d.items():
		if val is None:
			continue
		if isinstance(val, dict):
			val = cleanDict(val)
		if isinstance(val, (str, list, dict, tuple)) and len(val) == 0:
			continue
		result[key] = val
	return result

def mergeDicts(*parts):
	x = {}
	for part in parts:
		if part:
			x.update(part)
	return x

def excludeKeys(d, keys):
	if not d:
		return {}
	return {
		key: val
		for key, val in d.items()
		if key not in keys
	}

def focusFirstCustomParameterPage(o: 'COMP'):
	if o and o.customPages:
		o.par.pageindex = len(o.pages)

def detachTox(comp: 'COMP'):
	if not comp or comp.par['externaltox'] is None:
		return
	if not comp.par.externaltox and comp.par.externaltox.mode == ParMode.CONSTANT:
		return
	comp.par.reloadtoxonstart.expr = ''
	comp.par.reloadtoxonstart.val = False
	comp.par.externaltox.expr = ''
	comp.par.externaltox.val = ''

class Action:
	def __init__(self, func: Optional[Callable], args: list = None):
		self.func = func
		self.args = args

	def __call__(self, *args, **kwargs):
		if self.func:
			self.func(*self.args, *args, **kwargs)

def queueCall(action: Callable, *args, delayFrames=5, delayRef=None):
	run('args[0](*(args[1:]))', action, *args, delayFrames=delayFrames, delayRef=delayRef or root)
