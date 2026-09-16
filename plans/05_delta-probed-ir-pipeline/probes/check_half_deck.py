import json, numpy as np, amplitude_test as at
deck = json.load(open('results_dryrun/naphthalene_sym/deck.json'))
h = at.half_patterns(deck)
p0 = [p for p in deck['patterns'] if p['kind'] == 'two-mode'][0]
h0 = [p for p in h if p['index'] == p0['index']][0]
print('half patterns:', len(h))
print('amp', p0['amp'], '->', h0['amp'])
print('max|a|', max(abs(x) for x in p0['a']), '->', max(abs(x) for x in h0['a']))
print('holdout preserved:', p0['holdout'] == h0['holdout'])
print('kinds:', sorted(set(p['kind'] for p in h)))
print('index collision with parents:', len(set(p['index'] for p in h)) == len(h))
