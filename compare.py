import pandas as pd

best = pd.read_csv('submissions/0_99217.csv')
new = pd.read_csv('latest.csv')

best = best.fillna('')
new = new.fillna('')

cp = []

for idx, row in best.iterrows():
    before = best.loc[idx, 'name']
    after = new.loc[idx, 'name']

    if before != after:
        cp.append((before, after))

print(len(cp))

for each in cp:
    print(each)
    