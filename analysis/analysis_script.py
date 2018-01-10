sampleData = {
"0":[3,	0	,0	,-1, 0,	0,	-1,	0,	0,	1,	0,	-1,	],
"1":[6,	0	,1	,-1, 0,	0,	0	,0,	0,	1,	0,	-1,	],
"2":[3,	-1,	0	,0, 0,	0,	0	,0,	0,	1,	0,	-1,	],
"3":[3,	0	,-1,	0, 0,	0,	-1,	0,	0,	1,	0,	0	,],
"4":[3,	0	,-1,	-1, 0,	0,	0	,1,	0,	1,	0,	0	,],
"5":[3,	0	,-1,	-1, 0,	0,	0	,1,	0,	1,	0,	0	,],
"6":[1,	0	,-1,	-1, 0,	0,	-1,	0,	0,	1,	0,	0	,],
"7":[1,	1	,1	,-1, 0,	0,	-1,	1,	0,	1,	0,	1	,],
"8":[2,	0	,-1,	0, 0,	0,	0	,1,	1,	1,	0,	0	,],
"9":[3,	0	,0	,0, 0,	0,	0	,0,	1,	1,	0,	1	,],
}
genre = {u'other-genre': {u'ads': u'0.240140441',
  u'brokenlinks': u'0.496275523',
  u'domain': u'0.248023672',
  u'hyperlinks': u'0.480862371',
  u'imgratio': u'0.006922669',
  u'inlinks': u'0.728650503',
  u'langcount': u'0.008516245',
  u'lastmod': u'0.503201873',
  u'misspelled': u'0.289997645',
  u'outlinks': u'0.474079554',
  u'pageloadtime': u'0.022339502',
  u'responsive': u'0.006856424'}}

order  = ['domain', 'ads', 'imgratio', 'inlinks', 'pageloadtime', 'misspelled',
    'hyperlinks', 'brokenlinks', 'responsive', 'lastmod', 'langcount',
    'outlinks',]


scoreboard = []
for k,v in sampleData.items():
    score = 0
    for index in range(len(v)):
        score += float(genre["other-genre"][order[index]])*v[index]
    scoreboard.append(score)

print scoreboard
