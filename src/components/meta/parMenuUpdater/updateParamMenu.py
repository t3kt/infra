# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from typing import Dict, List, Set

def update():
	try:
		host = parent().par.Hostop.eval()
		if not host:
			return
		dat = parent().par.Table.eval()
		if not dat or dat.numRows < 2:
			return
		names = [c.val for c in dat.col('name')[1:]]
		labels = [c.val for c in dat.col('label')[1:]]
		pars = host.pars(*(mod.tdu.split(parent().par.Param)))
		for par in pars:
			par.menuNames = names
			par.menuLabels = labels
		_applyParamStateExprs(host, pars, dat)
	except BaseException as e:
		print(f'Error attempting to update paramMenu in {parent()}: {e}')
		raise e

def _applyParamStateExprs(host: 'OP', menuPars: 'List[Par]', dat: 'DAT'):
	if not menuPars or not parent().par['Manageparamstates'] or not dat.col('params') or dat.numRows < 2:
		print(f'Not updating enableExprs in {host}')
		return
	if len(menuPars) > 1:
		raise Exception('Unable to manage param states when there are multiple menu parameters')
	menuPar = menuPars[0]
	managedParNames = set()  # type: Set[str]
	valuesByParName = {}  # type: Dict[str, Set]
	for i in range(1, dat.numRows):
		names = tdu.split(dat[i, 'params'])
		val = dat[i, 'name'].val
		if names:
			pars = host.pars(*names)
			for par in pars:
				managedParNames.add(par.name)
				if par.name not in valuesByParName:
					valuesByParName[par.name] = set()
				valuesByParName[par.name].add(val)
	for name in managedParNames:
		par = host.par[name]
		if par is None:
			continue
		vals = list(sorted(valuesByParName[name]))
		if len(vals) == 1:
			expr = f"me.par.{menuPar.name} == '{vals[0]}'"
		else:
			expr = f"me.par.{menuPar.name} in ({','.join(repr(v) for v in vals)})"
		par.enableExpr = expr

def onValueChange(par, prev):
	if par.name == 'Autoupdate' and par:
		update()

def onTableChange(dat):
	update()

def onPulse(par):
	if par.name == 'Update':
		update()
