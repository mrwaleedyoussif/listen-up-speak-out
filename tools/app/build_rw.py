#!/usr/bin/env python3
"""Reading and Writing department: turns the "English Pathway" unit files (strand C, one JSON per unit) into the data
the department page (www/gv, shared with Language Usage) loads.
    python3 -I tools/app/build_rw.py SRC        # SRC/json/L<level>U<unit>.json, kept outside the repository
Output: www/gv/data/reading_writing/index.js and units/LxxUy.js; the strand is switched on in www/gv/data/strands.js.
Changes on the way in: multiple-choice keys become the answer text (as the page expects); ordering tasks, timed
reading and find-the-evidence tasks get the fields their on-screen activities need; image and video production briefs
(for the materials team) are left out; levels 9 to 12 are listed as "Soon"."""
import json, os, re, sys, glob
SRC = os.path.abspath(sys.argv[1]); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'www', 'gv', 'data', 'reading_writing'); os.makedirs(os.path.join(OUT, 'units'), exist_ok=True)
STAGE = {'controlled': 'Controlled practice', 'guided': 'Guided practice', 'freer': 'Freer practice', 'production': 'Writing'}
TYPE = {'timed_reading': 'Timed reading', 'organizer': 'Organizer', 'writing': 'Writing', 'highlight': 'Find the evidence', 'order': 'Put in order'}
def key_to_text(it, where):
    o = it.get('options'); a = it.get('answer')
    if o and isinstance(a, str) and len(a) == 1 and a in 'abcdefgh':
        i = 'abcdefgh'.index(a); assert i < len(o), (where, a, o); it['answer'] = o[i]
    elif o: assert a in o, (where, a, o)
def sentences(body):
    out = []
    for para in body.split('\n'):
        para = para.strip()
        if not para: continue
        out += [s.strip() for s in re.sub(r'([.!?…]["”’\')]?)\s+(?=["“‘(A-Z0-9])', '\\1\x00', para).split('\x00') if s.strip()]
    return out
stats = {}; levels = {}
for f in sorted(glob.glob(os.path.join(SRC, 'json', 'L*U*.json'))):
    d = json.load(open(f, encoding='utf-8')); lv, un = d['level'], d['unit']; assert d['strand'] == 'reading_writing'
    for L in d['lessons']:
        texts = {t['id']: t for t in L['texts']}; alltexts = {t['id']: t for x in d['lessons'] for t in x['texts']}
        for t in L['texts']: t.pop('annotations', None) if not t.get('annotations') else None
        L['images'] = [{'id': im['id'], 'prompt': im.get('alt', '')} for im in L.get('images', [])]   # the long art briefs stay with the materials team
        L['audio'] = [{'id': a['id'], 'script': a.get('script', '')} for a in L.get('audio', [])]
        for k in ('ccss', 'source_alignment', 'sat_domain', 'duration_min'): L.pop(k, None)
        g = L.get('game') or {}   # on screen the game is a quick quiz on the lesson; the classroom version stays in the rules
        L['game'] = {'name': g.get('name') or 'Lesson game', 'mechanic': 'timed_quiz', 'rules': ['On this screen: answer the lesson questions as fast as you can.'] + (['In class: ' + g['mechanic']] if g.get('mechanic') else []) + list(g.get('rules') or []), 'data': []}
        for a in L['activities']: stats[a['type']] = stats.get(a['type'], 0) + 1
    # activities: labels, keys and the extra fields the on-screen activities need
    src = json.load(open(f, encoding='utf-8'))
    for L, L0 in zip(d['lessons'], src['lessons']):
        alltexts = {t['id']: t for x in d['lessons'] for t in x['texts']}
        for a, a0 in zip(L['activities'], L0['activities']):
            ty = a0['type']; label = TYPE.get(ty) or STAGE.get(a0.get('stage')) or 'Practice'
            a['instructions'] = label + ': ' + a0['instructions']
            if ty == 'writing' and a0.get('prompt'): a['instructions'] += ' ' + a0['prompt']
            if ty == 'order':
                a['type'] = 'sequence'
                for it in a['items']:   # the page compares the texts in order, so a repeated word may sit in either place
                    opts = it.pop('options'); target = [opts['abcdefgh'.index(x.strip())] for x in it['answer'].split(',')]
                    if sorted(target) != sorted(opts): stats['order: key does not use every part'] = stats.get('order: key does not use every part', 0) + 1; target = None
                    if target: it['parts'] = opts; it['target'] = target; it['answer'] = (' ' if all(len(x.split()) <= 2 for x in opts) else ' → ').join(target)
                    else: it['q'] += ' (' + ' / '.join(opts) + ')'; it['answer'] = it.get('explanation') or it['answer']
            elif ty == 'timed_reading':
                for it in a['items']:
                    t = alltexts[it['q']]; it['title'] = t['title']; it['body'] = t['body']; it['words'] = int(it['answer']); it['limit'] = a0.get('time_limit_sec') or 0
                    it['q'] = 'Read “%s”.' % t['title']; it['answer'] = '%d words' % it['words']
            elif ty == 'highlight':
                for it in a['items']:
                    if it.get('options'): key_to_text(it, f)
                    elif it.get('text_id') in alltexts: it['sentences'] = sentences(alltexts[it['text_id']]['body'])
            else:
                for it in a['items']:
                    if it.get('options'): key_to_text(it, f)
            if ty == 'writing':
                a['items'][-1]['_w'] = {'checklist': a0.get('checklist') or [], 'min': a0.get('min_words'), 'max': a0.get('max_words')}
        for it in L['exit_quiz']: key_to_text(it, f)
    test, writing = [], None
    for it in d['unit_test']:
        if it.get('text_id'): stats['unit-test questions on a passage that is not in the unit file (left out)'] = stats.get('unit-test questions on a passage that is not in the unit file (left out)', 0) + 1; continue
        if it.get('options'): key_to_text(it, f); it['_part'] = it.pop('section', ''); test.append(it)
        else: writing = {'task': it['q'], 'model': it['answer'], 'marks': it.get('points') or 20}
    d['unit_test'] = test
    if writing: d['unit_writing'] = writing
    name = 'L%02dU%d' % (lv, un)
    open(os.path.join(OUT, 'units', name + '.js'), 'w', encoding='utf-8').write('PathwayData.put("data/reading_writing/units/%s.json",%s);\n' % (name, json.dumps(d, ensure_ascii=False, separators=(',', ':'))))
    levels.setdefault(lv, {'level': lv, 'cefr': d['cefr'], 'units': []})['units'].append({'unit': un, 'theme': d['theme'], 'theme_ar': d.get('theme_ar', ''), 'eq': d['essential_question'], 'eq_ar': d.get('essential_question_ar', ''),
        'file': 'units/%s.json' % name, 'lessons': [{'id': L['id'], 'title': L['title']} for L in d['lessons']], 'words': len(d.get('core_words', []))})
idx = {'strand': 'reading_writing', 'title': 'Reading and Writing', 'code': 'RW', 'levels': [levels.get(n) or {'level': n, 'cefr': '', 'units': [], 'soon': True} for n in range(1, 13)], 'tests': {}}
for L in idx['levels']: L['units'].sort(key=lambda u: u['unit'])
open(os.path.join(OUT, 'index.js'), 'w', encoding='utf-8').write('PathwayData.put("data/reading_writing/index.json",%s);\n' % json.dumps(idx, ensure_ascii=False, separators=(',', ':')))
p = os.path.join(ROOT, 'www', 'gv', 'data', 'strands.js'); s = open(p, encoding='utf-8').read()
s2 = re.sub(r'("id":"reading_writing","title":")[^"]*(".*?"index":"data/reading_writing/index.json","enabled":)(false|true)', r'\1Reading and Writing\2true', s); assert s2 != s or '"Reading and Writing"' in s; open(p, 'w', encoding='utf-8').write(s2)
size = sum(os.path.getsize(os.path.join(OUT, 'units', x)) for x in os.listdir(os.path.join(OUT, 'units')))
print('units', sum(len(L['units']) for L in idx['levels']), {L['level']: len(L['units']) for L in idx['levels']}, '| activities', stats, '| %.1f MB' % (size / 1e6))
