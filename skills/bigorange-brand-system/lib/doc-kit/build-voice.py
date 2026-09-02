import markdown, re, html
md=open('brand-voice-guide.md').read()
# strip H1 if present
md=re.sub(r'^# .*\n','',md,count=1)
body=markdown.markdown(md,extensions=['tables','sane_lists'])
# Section-specific decoration
def wrap_section(h2title, transform):
    global body
    m=re.search(r'(<h2>'+re.escape(h2title)+r'</h2>)(.*?)(?=<h2>|$)',body,re.S)
    if m: body=body[:m.start(2)]+transform(m.group(2))+body[m.end(2):]
# one sentence
wrap_section('The voice in one sentence', lambda s: re.sub(r'<p>(.*?)</p>', r'<p class="one">\1</p>', s, count=1))
# pillars: group each h3 with following content into .pillar cards
def pillars(s):
    parts=re.split(r'(?=<h3>)',s); head=parts[0]; cards=[]
    for i,p in enumerate(parts[1:]):
        p=re.sub(r'<h3>(.*?)</h3>', r'<div class="n">%02d</div><h3>\1</h3>'%(i+1), p, count=1)
        cards.append('<div class="pillar">'+p+'</div>')
    return head+'<div class="pillars">'+''.join(cards)+'</div>'
wrap_section('Voice pillars', pillars)
# before/after pairs
def ba(s):
    out=[]; items=re.findall(r'<p>(?:<strong>)?Before:?(?:</strong>)?\s*(.*?)</p>\s*<p>(?:<strong>)?After:?(?:</strong>)?\s*(.*?)</p>',s,re.S)
    if not items: return s
    lead=s.split('<p>',1)[0]
    for b,a in items: out.append(f'<div class="ba"><div class="b"><div class="k">Before</div>{b}</div><div class="a"><div class="k">After</div>{a}</div></div>')
    # keep any h3 sub-labels out; simple approach: return lead + pairs
    return lead+''.join(out)
wrap_section('Before and after', ba)
wrap_section('Voice QA checklist', lambda s: '<div class="qa">'+s+'</div>')
def prompt(s):
    m=re.search(r'<pre><code>(.*?)</code></pre>',s,re.S)
    if m: return s[:m.start()]+'<div class="prompt"><div class="k">Paste this in</div>'+html.escape(html.unescape(m.group(1))).replace('\n','<br>')+'</div>'+s[m.end():]
    bq=re.search(r'<blockquote>(.*?)</blockquote>',s,re.S)
    if bq: return s[:bq.start()]+'<div class="prompt"><div class="k">Paste this in</div>'+bq.group(1)+'</div>'+s[bq.end():]
    return s
wrap_section('AI and outside-writer instructions', prompt)
wrap_section('Sources', lambda s: '<div class="src">'+s+'</div>')
body=body.replace('—',', ')
page=f'''<!doctype html><html><head><meta charset="utf-8"><title>BigOrange Brand Voice Guide</title><link rel="stylesheet" href="theme.css"><link rel="stylesheet" href="voice.css"></head><body>
<section class="page vcover cover-only">
  <img class="logo" src="assets/bigorange-logo-white.png" alt="BigOrange.Marketing">
  <div class="big">Brand<br>Voice<small>How BigOrange sounds, and how to write like it.</small></div>
  <p class="sub">A working guide for the BigOrange team, outside writers, and the AI tools that draft for us. Read it once, then keep the checklist nearby.</p>
  <div class="ink"></div><div class="ink2"></div>
  <div class="foot">Version 1.0 · September 2026<b>Prepared by Dillon Mohr for BigOrange.Marketing</b></div>
</section>
<div class="body-only article vbody">{body}</div></body></html>'''
open('voice.html','w').write(page); print('voice.html', len(page))
