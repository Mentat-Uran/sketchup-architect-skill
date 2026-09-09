#!/usr/bin/env python3
"""Validate an architectural ledger; no geometry generation or app control."""
import argparse
from collections import defaultdict, deque
import json
import math
from pathlib import Path
import sys


def check(plan, audit=None):
    errors, warnings = [], []

    def number(value, label, positive=False):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            errors.append(label + ': expected finite number')
            return 0.0
        if value < 0 or (positive and value <= 0):
            errors.append(label + ': must be ' + ('positive' if positive else 'nonnegative'))
        return float(value)

    def unique(items, label):
        result = {}
        for item in items:
            key = item.get('id')
            if not isinstance(key, str) or not key.strip() or key in result:
                errors.append(label + ': missing/duplicate id ' + str(key))
            else:
                result[key] = item
        return result

    if plan.get('schema_version') != 1 or plan.get('units') != 'm':
        errors.append('schema_version must be 1 and ledger units must be m (areas m2)')
    if not isinstance(plan.get('project_id'), str) or not plan['project_id'].strip():
        errors.append('project_id is required')
    if type(plan.get('revision')) is not int or plan['revision'] < 0:
        errors.append('revision must be a nonnegative integer')
    tolerance = number(plan.get('tolerance_fraction', 0.03), 'tolerance_fraction')
    if tolerance > 0.10:
        errors.append('tolerance_fraction above 0.10 hides substantial mismatch; resolve the design/measurement basis')
    target = number(plan.get('target_gfa_m2'), 'target_gfa_m2', positive=True)
    levels = unique(plan.get('levels', []), 'levels')
    spaces = unique(plan.get('spaces', []), 'spaces')
    if not levels or not spaces:
        errors.append('at least one level and one space are required')
    gross, totals, nets = {}, defaultdict(float), {}
    for lid, level in levels.items():
        gross[lid] = number(level.get('gfa_m2'), lid + '.gfa_m2')
        totals[lid] += number(level.get('allowance_m2', 0), lid + '.allowance_m2')
        elevation = level.get('elevation_m')
        if type(elevation) not in (int, float) or not math.isfinite(elevation):
            errors.append(lid + '.elevation_m must be a finite number')
    for sid, space in spaces.items():
        lid = space.get('level')
        area = number(space.get('area_m2'), sid + '.area_m2', positive=True)
        if lid not in levels:
            errors.append(sid + ': unknown level ' + str(lid))
        if not space.get('external', False):
            totals[lid] += area
            nets[sid] = area
        if space.get('requires_access') is False and not space.get('access_exclusion_reason'):
            errors.append(sid + ': excluded access requires access_exclusion_reason')

    def compare(actual, wanted, label):
        if abs(actual - wanted) > max(0.01, abs(wanted) * tolerance):
            errors.append('%s: %.3f versus %.3f m2 exceeds tolerance' % (label, actual, wanted))

    total_gfa = sum(gross.values())
    compare(total_gfa, target, 'total GFA / target')
    for lid, value in gross.items():
        compare(totals[lid], value, lid + ' net + allowance / GFA')
    graph = defaultdict(set)
    for conn in plan.get('connections', []):
        a, b = conn.get('from'), conn.get('to')
        if a not in spaces or b not in spaces or a == b:
            errors.append('connection has unknown or identical endpoints: ' + str(conn))
            continue
        if spaces[a]['level'] != spaces[b]['level'] and conn.get('kind') not in ('stair', 'lift', 'ramp'):
            errors.append('cross-level connection needs stair/lift/ramp: ' + a + ' -> ' + b)
        graph[a].add(b)
        graph[b].add(a)
    entries = [sid for sid, space in spaces.items() if space.get('entry') is True]
    if not entries:
        errors.append('at least one entry node is required')
    reached, queue = set(entries), deque(entries)
    while queue:
        for sid in graph[queue.popleft()]:
            if sid not in reached:
                reached.add(sid)
                queue.append(sid)
    for sid, space in spaces.items():
        if space.get('requires_access', True) and sid not in reached:
            errors.append('no access route from an entry: ' + sid)
    mode = 'plan_only'
    if audit is not None:
        mode = 'plan_and_runtime_measurements'
        if audit.get('schema_version') != 1 or audit.get('kind') != 'sketchup_architect_audit':
            errors.append('unrecognized audit schema')
        for key in ('project_id', 'revision'):
            if audit.get(key) != plan.get(key):
                errors.append('audit ' + key + ' does not match ledger')
        if audit.get('complete') is not True:
            errors.append('runtime audit is incomplete')
        errors.extend('model: ' + str(x) for x in audit.get('errors', []))
        warnings.extend('model: ' + str(x) for x in audit.get('warnings', []))
        quantities = audit.get('quantities', {})
        for label, expected, field in [('GFA', gross, 'gfa_m2_by_level'), ('net', nets, 'net_m2_by_space')]:
            actuals = quantities.get(field, {})
            for key, wanted in expected.items():
                if key not in actuals:
                    errors.append('missing measured ' + label + ': ' + key)
                else:
                    compare(number(actuals[key], 'measured ' + key), wanted, 'measured ' + label + ' ' + key)
            for key in actuals.keys() - expected.keys():
                errors.append('unaccounted measured ' + label + ': ' + key)
    warnings.append('Connectivity is an intent graph; physical paths, overlap, site fit, headroom, accessibility and code compliance require separate review.')
    return {'ok': not errors, 'mode': mode, 'gfa_m2': total_gfa, 'target_gfa_m2': target,
            'area_balance_m2': {lid: round(totals[lid] - gross[lid], 5) for lid in levels},
            'reachable_spaces': sorted(reached), 'errors': errors, 'warnings': warnings}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('plan', type=Path)
    p.add_argument('--audit', type=Path)
    args = p.parse_args()
    try:
        result = check(json.loads(args.plan.read_text()), json.loads(args.audit.read_text()) if args.audit else None)
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        result = {'ok': False, 'errors': ['Invalid input: ' + str(exc)]}
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    return 0 if result['ok'] else 2


if __name__ == '__main__':
    sys.exit(main())
