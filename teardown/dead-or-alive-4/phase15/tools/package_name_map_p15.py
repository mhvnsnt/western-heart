#!/usr/bin/env python3
"""DOA4 phase 15 Job 1c: join the containment map with the package
spans -> PACKAGE-NAME-MAP rows. Rule (per task): where a package's
range falls inside one ISO entry's contained range, assign that
entry's name. Primary assignment = the entry whose contained
segment(s) contain the package's xpr2_offset; secondary evidence =
fraction of the package's graph span covered by that entry's
segments, and the list of other entries the span crosses.
Output: package_name_map_p15.json + a markdown table on stdout."""
import json, os

SCR = '/home/hatch/workspace/_doa4p2-scratch/p15'

def main():
    cm = json.load(open(os.path.join(SCR, 'containment_map_p15.json')))
    ps = json.load(open(os.path.join(SCR, 'package_spans_p15.json')))
    out = {}
    for vol in ('chrone', 'chrtwo', 'chrthree'):
        entries = cm[vol]['entries']
        def entry_at(moff):
            for e in entries:
                for (eo, mo, ln) in e['segments']:
                    if mo <= moff < mo + ln:
                        return e['name']
            return None
        rows = []
        for p in ps[vol]:
            name = entry_at(p['xpr2_offset'])
            span = (p['span_end'] - p['xpr2_offset']) if p['span_end'] else None
            frac = None; cross = []
            if span:
                cov = 0
                for e in entries:
                    for (eo, mo, ln) in e['segments']:
                        a = max(mo, p['xpr2_offset']); b = min(mo + ln, p['span_end'])
                        if b > a:
                            if e['name'] == name: cov += b - a
                            else: cross.append(e['name'])
                frac = round(cov / span, 4)
            rows.append({'package': p['package'], 'xpr2_offset': p['xpr2_offset'],
                         'span_end': p['span_end'], 'assigned_entry': name,
                         'span_frac_in_assigned': frac, 'crosses': sorted(set(cross))})
            print(vol, p['package'], '->', name, 'frac', frac, 'crosses', sorted(set(cross)))
        out[vol] = rows
    json.dump(out, open(os.path.join(SCR, 'package_name_map_p15.json'), 'w'), indent=1)
    print('WROTE package_name_map_p15.json')

if __name__ == '__main__':
    main()
