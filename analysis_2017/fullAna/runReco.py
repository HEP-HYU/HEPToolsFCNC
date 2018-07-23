#!/usr/bin/python
from ROOT import TFile, TChain, gSystem
import os, sys
gROOT.SetBatch(True)

file_path = sys.argv[1]
name = sys.argv[2]

test = os.listdir("./temp")
for item in test:
  if item.endswith(name + ".root"):
    print 'Previous verion of histogram ' + name + '.root exists!! Please remove them first.'
    dupl = true

def runAna(file_path, name):
  print 'processing ' + file_path
  chain = TChain("fcncLepJets/tree","events")
  chain.Add(file_path)
  chain.Process("MyAnalysis.C+",name)
  #print chain.GetCurrentFile().GetName()

  f = TFile.Open(file_path, "READ")

  ## save Event Summary histogram ##
  out = TFile("temp/hist_"+name+".root","update")
  hevt = f.Get("fcncLepJets/EventInfo")
  hevt.Write()
  out.Write()
  out.Close()

if not dupl: runAna(file_path, name)