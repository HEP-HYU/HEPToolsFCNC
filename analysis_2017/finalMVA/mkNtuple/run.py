#!/usr/bin/python
from ROOT import *
import os, sys
from root_numpy import tree2array
import glob
import pandas as pd
import deepdish.io as io
gROOT.SetBatch(True)

ver = "01"
input_filename = sys.argv[1]
output_filename = sys.argv[2]
syst = ["","jecup","jecdown","jerup","jerdown"]
syst2 = ["TuneCP5up","TuneCP5down","hdampup","hdampdown"] #dedecative samples exist

for syst_ext in syst + syst2:
  if not os.path.exists( "root_" + syst_ext ):
    print "No folder"
    sys.exit()
  if not os.path.exists( "hdf_" + syst_ext ):
    print "No folder"
    sys.exit()

def runAna(input_filename, output_filename):
  print 'processing ' + input_filename

  for syst_ext in syst + syst2:
    if   ("Run2017" in output_filename) and syst_ext != "": continue
    elif (syst_ext in syst2) and not (syst_ext in output_filename): continue
    elif (syst_ext in syst) and any(tmp in output_filename for tmp in syst2): continue
    else:
      if (syst_ext in syst2): output_filename = output_filename.replace(syst_ext,"")

      chain = TChain("fcncLepJets/tree","events")
      chain.Add(input_filename)
      chain.Process("makeTuple.C+", ver + syst_ext + '_' + output_filename)

      if os.path.isfile("root_" + syst_ext + "/finalMVA_" + output_filename + ".root"):
        f = TFile.Open("root_" + syst_ext + "/finalMVA_" + output_filename + ".root")
        t = f.Get("tree")
        if t.GetEntries() != 0:
          a = tree2array(t)
          df = pd.DataFrame(a)
          io.save("hdf_" + syst_ext + "/finalMVA_" + output_filename + ".h5", df)
        else: os.remove("root_" + syst_ext + "/finalMVA_" + output_filename + ".root")

runAna(input_filename, output_filename)