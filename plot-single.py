import json
import matplotlib.pyplot as plt
import sys
import argparse

freqs = []
amps = {}

ap = argparse.ArgumentParser()
ap.add_argument("-d1", "--data1", required=True)
ap.add_argument("-d2", "--data2", required=True)
ap.add_argument("-c", "--control", required=True)
ap.add_argument("-n", "--number", required=True)
ap.add_argument("-o", "--output", required=False)
args = vars(ap.parse_args())
fig, axes = plt.subplots(1, 1, figsize=(20, 16))

with open(args['data1']) as fileo:
  data1 = json.load(fileo)
  freqs1 = data1['freqs']
  amps1 = data1
with open(args['data2']) as fileo:
  data2 = json.load(fileo)
  freqs2 = data2['freqs']
  amps2 = data2

with open(args['control']) as fileo:
  data = json.load(fileo)
  for i in range(9):
    for j in range(len(amps1[str(i)])):
      amps1[str(i)][j] -= data[str(i)][j]
    for j in range(len(amps2[str(i)])):
      amps2[str(i)][j] -= data[str(i)][j]

#for n in range(9):
#  plt.subplot(3, 3, n+1)
plt.grid(color='gray', linestyle='-', linewidth=0.25)
  #plt.gca().set_ylim([83500,87000])
plt.plot(freqs1, amps1[args['number']], linewidth=0.5, label='Penrose')
plt.plot(freqs2, amps2[args['number']], linewidth=0.5, label='Quasicrystal')
#  if(n % 3 == 0):
plt.ylabel("Amplitude")
#  if(n > 5):
plt.xlabel("Frequency")
#  else:
#    plt.xlabel(n)
plt.tight_layout()
plt.legend(loc='lower right', prop={'size': 24})
if(args['output']):
  plt.savefig(args['output'], dpi=300)
plt.show()
