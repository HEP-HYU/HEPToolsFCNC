cat ../../commonTools/file_top.txt | xargs -i -P$(nproc) -n2 python run_top.py STFCNC
cat ../../commonTools/file_other.txt | xargs -i -P$(nproc) -n2 python run_other.py STFCNC
cat ../../commonTools/file_top.txt | xargs -i -P$(nproc) -n2 python run_top.py TTFCNC
cat ../../commonTools/file_other.txt | xargs -i -P$(nproc) -n2 python run_other.py TTFCNC
cat ../../commonTools/file_top.txt | xargs -i -P$(nproc) -n2 python run_top.py TTBKG
cat ../../commonTools/file_other.txt | xargs -i -P$(nproc) -n2 python run_other.py TTBKG
