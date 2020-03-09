import serial
import numpy as np
import scipy as sy
import scipy.fftpack as syfp
import pylab as pyl 
import time
import Queue
import sys
from threading import Thread
import visa
import atexit
from nfft import nfft
import json

trial_freqs = []

device = visa.ResourceManager().open_resource('USB::0x0699::0x0353::1633778::INSTR')
 
streams = [serial.Serial('COM%d' % n) for n in range(3, 12)]

for stream in streams:
  stream.flushInput()

def exit_handle():
  device.write('OUTPut2:STATe OFF')
atexit.register(exit_handle)

#def avg(xs):
#    xs.sort(key=lambda x: x[0])
#    if(len(xs) % 2 == 0):
#        return (xs[len(xs)/2][1] + xs[len(xs)/2+1][1])/2
#    else:
#        return xs[len(xs)/2][1]

# [(freq, amplitude)] -> amplitude
def avg(xs):
  s = 0;
  for x in xs:
    s += abs(x[1])
  return s/len(xs)

def y_or_n(question):
  reply = str(raw_input(question+' (y/n): ')).lower().strip()
  if reply[0] == 'y':
    return True
  if reply[0] == 'n':
    return False
  else:
    return y_or_n("Please enter [y]es or [n]o...")
 
def collect_data(t0, n, results, stream):
  data = []
  while(stream.in_waiting == 0):
    stream.write(254)
  dt = time.time()
  while(True):
    row_bytes = stream.readline()
    row = row_bytes[0:len(row_bytes)-2].decode("utf-8")
    if(len(row) == 0):
        continue
    if(row[0] == "#"):
      data.append(list(map(float, row[1:].split(" "))))
    if(row[0] == "$"):
      results[n] = (0, data)
      #results[n] = (int(round(dt * 1000)) - t0, data)
      return
 
def collect_data_s(t0, results, streams):
  data = list([ [] for stream in streams ])
  ready = list([ False for stream in streams ])
  while(False in ready):
    n = 0
    for stream in streams:
      if(stream.in_waiting == 0):
        stream.write(254)
      else:
        ready[n] = True
      n=n+1
  done = list([ False for stream in streams ])
  while(False in done):
    n = 0
    for stream in streams:
      row_bytes = stream.readline()
      row = row_bytes[0:len(row_bytes)-2].decode("utf-8")
      #if(len(row) == 0):
      #  continue
      if(len(row) > 0 and row[0] == "#"):
        data[n].append(list(map(float, row[1:].split(" "))))
      if(len(row) > 0 and row[0] == "$"):
        results[n] = (0, data[n])
        #results[n] = (int(round(dt * 1000)) - t0, data)
        done[n] = True
      n=n+1

def run_trial_smt(streams):
  results = {}
  threads = []
  n = 0
  t0 = int(round(time.time() * 1000))
  for s in streams:
    threads.append(Thread(target = collect_data, args = (t0, n, results, s)))
    n=n+1
  for t in threads:
    t.start()
  for t in threads:
    t.join()
  return results
 
def run_trial(streams):
  results = {}
  t0 = int(round(time.time() * 1000))
  collect_data_s(t0, results, streams)
  return results

def process_trial(trial):
  entries = []
  for sensor, (dt, data) in trial.items():
    x, y = np.array(data).T
    FFT = sy.fft(y)
    #FFT = nfft(x, y)
    freqs = syfp.fftfreq(y.size, d=(x[1]-x[0]))
    x = sorted(zip(freqs, FFT), key=lambda x: abs(x[1]), reverse=True)[2]
    #if(y_or_n("%d: inspect this frequency?" % abs(x[0]))):
    #  plot_data_intermediate(freqs, FFT)
    print("freq: %d, amp: %d" % (abs(x[0]), abs(x[1])))
    entries.append((sensor, abs(x[0]), abs(x[1])))
  return entries

def plot_data_intermediate(freqs, FFT):
  #pyl.plot(freqs, sy.log10(FFT), 'x')
  pyl.plot(freqs, FFT, 'x')
  xy = sorted(zip(freqs, FFT), key=lambda x: abs(x[1]), reverse=True)[2]
  pyl.annotate('(%s, %s)' % xy, xy=xy, textcoords='data')
  pyl.xlabel("Frequency")
  pyl.ylabel("Amplitude")
  pyl.tight_layout()
  pyl.show()

def plot_data(freqs, amps):
  pyl.subplot(3,3,1);

def do_freq(freq, trial_count=3):
  device.write('SOURce2:FREQuency:FIXed %dHz' % freq)
  trials = {}
  for trial in range(1, trial_count + 1):
    print("Running trial %d for %dHz" % (trial, freq))
    ts = process_trial(run_trial(streams))
    for t in ts:
      trials.setdefault(t[0], []).append((t[1], t[2]))
  averages = {}
  for sensor, data in trials.items():
    averages.setdefault(sensor, []).append(avg(data))
  return averages

def run_experiment(lower_freq, upper_freq, step=10):
  freqs = []
  amps = {}
  device.write('OUTPut2:STATe ON')
  device.write('SOURce2:FREQuency:FIXed %dHz' % lower_freq)
  time.sleep(10) # very important
  for freq in range(lower_freq, upper_freq, step):
    freqs.append(freq)
    for sensor, average in do_freq(freq).items():
      amps.setdefault(sensor, []).append(average)
  device.write('OUTPut2:STATe OFF')

  with open("C:/Users/Ed Rietman/Desktop/Control-1000-10000-90-uniform.json", "w") as file:
    file.write(json.dumps(freqs))
    file.write("\r\n")
    file.write(json.dumps(amps))

  sensors = amps.keys()
  pyl.tight_layout()
  for i in range(len(freqs)):
    for j in range(len(sensors)):
      pyl.subplot(3, 3, j+1)
      pyl.plot(freqs, amps[sensors[j]])
      pyl.xlabel("Frequency")
      pyl.ylabel("Amplitude")
  pyl.show()

delay = 10
print("delaying %d seconds..." % delay)
time.sleep(delay)

run_experiment(1000, 3000, step=10)
#run_experiment(500, 1100, step=10)
