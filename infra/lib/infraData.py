from dataclasses import dataclass, asdict
import json

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

@dataclass
class DataObjectBase:
	def toObj(self):
		return asdict(self)

	@classmethod
	def fromObj(cls, obj):
		# noinspection PyArgumentList
		return cls(**obj)

	def toJson(self, minify=True):
		obj = self.toObj()
		return toJson(obj, minify)

def toJson(obj, minify=True):
	return '{}' if not obj else json.dumps(
		obj,
		indent=None if minify else '  ',
		separators=(',', ':') if minify else (', ', ': '),
		sort_keys=True,
	)
