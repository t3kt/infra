# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

def initHost():
	filterOp = parent()
	hostOp = filterOp.par.Parfilterop.eval()
	if not hostOp:
		return
	prefix = filterOp.par.Installedlabelprefix.eval()
	page = hostOp.appendCustomPage('Param Filter')
	fp = filterOp.par.Parfilterenable
	page.appendToggle(fp.name, label=prefix + fp.label)
	fp = filterOp.par.Parfiltertype
	p = page.appendMenu(fp.name, label=prefix + fp.label)[0]
	p.menuNames = fp.menuNames
	p.menuLabels = fp.menuLabels
	p.default = fp.default
	_copyFloatPar(page, filterOp.par.Parfilterwidth, prefix)
	_copyFloatPar(page, filterOp.par.Parfilterlag1, prefix)
	_copyFloatPar(page, filterOp.par.Parfilterovershoot1, prefix)
	_copyFloatPar(page, filterOp.par.Parfiltercutoff, prefix)
	_copyFloatPar(page, filterOp.par.Parfilterspeedcoeff, prefix)
	_copyFloatPar(page, filterOp.par.Parfilterslopecutoff, prefix)
	_copyFloatPar(page, filterOp.par.Parfilterreset, prefix)
	_copyFloatPar(page, filterOp.par.Parfilterresetpulse, prefix)

	exprPrefix = 'op("{}").par.'.format(filterOp.relativePath(hostOp))
	for p in filterOp.customPages[0].pars:
		p.bindExpr = exprPrefix + p.name

def _copyFloatPar(page: 'Page', src: 'Par', prefix: str):
	sourceTuplet = src.tuplet
	parTuplet = page.appendFloat(src.tupletName, label=prefix + src.label, size=len(sourceTuplet))
	for i, srcp in enumerate(sourceTuplet):
		for a in (
				'default', 'normMin', 'normMax',
				'clampMin', 'clampMax', 'min', 'max',
				'enableExpr',
		):
			setattr(parTuplet[i], a, getattr(srcp, a))
