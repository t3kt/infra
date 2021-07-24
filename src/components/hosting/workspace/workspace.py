from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class Workspace:
	def __init__(self, ownerComp: 'COMP'):
		self.ownerComp = ownerComp

@dataclass
class WorkspaceSpec:
	workspaceFile: Optional[Path]

	# If true, automatically scan sceneFolder to find scenes.
	# Otherwise rely on a predetermined list of sceneFiles
	autoScenes: bool

	# For when the workspace uses a folder for scenes, or as
	# the root path when using sceneFiles
	sceneFolder: Optional[Path]

	# For when the workspace uses a list of scene files
	sceneFiles: Optional[List[Path]]
	pass
