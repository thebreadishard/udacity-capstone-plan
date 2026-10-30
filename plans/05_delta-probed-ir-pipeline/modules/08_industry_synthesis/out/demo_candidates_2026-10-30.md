# Demo candidates: unseen by the network, within half an hour (TASKS 152)

Laptop estimates at 6 threads (`m08.runtime`); seen-ness by canonical SMILES (`m08.seen`). Short list: 14 of 36.

| name | SMILES | atoms | basis functions | est. minutes | the network | short list |
|---|---|---|---|---|---|---|
| anisole | `COc1ccccc1` | 16 | 136 | 14 | in the catalogue (B_3f48f24c66) but not among the molecules the network trained on | yes |
| benzofuran | `c1ccc2occc2c1` | 15 | 147 | 18 | in the catalogue (A_fead28d796) but not among the molecules the network trained on | yes |
| benzoxazole | `c1ccc2ocnc2c1` | 14 | 145 | 18 | not in the catalogue: the network has not seen it | yes |
| benzimidazole | `c1ccc2[nH]cnc2c1` | 15 | 147 | 18 | not in the catalogue: the network has not seen it | yes |
| benzothiazole | `c1ccc2scnc2c1` | 14 | 149 | 19 | not in the catalogue: the network has not seen it | yes |
| benzothiophene | `c1ccc2sccc2c1` | 15 | 151 | 20 | in the catalogue (A_9d7c66d274) but not among the molecules the network trained on | yes |
| quinoxaline | `c1ccc2nccnc2c1` | 16 | 162 | 25 | in the catalogue (A_7aa232d4e9) but not among the molecules the network trained on | yes |
| quinazoline | `c1ccc2ncncc2c1` | 16 | 162 | 25 | in the catalogue (A_d295f2fa80) but not among the molecules the network trained on | yes |
| cinnoline | `c1ccc2nnccc2c1` | 16 | 162 | 25 | not in the catalogue: the network has not seen it | yes |
| phthalazine | `c1ccc2cnncc2c1` | 16 | 162 | 25 | not in the catalogue: the network has not seen it | yes |
| 1,5-naphthyridine | `c1cnc2cccnc2c1` | 16 | 162 | 25 | not in the catalogue: the network has not seen it | yes |
| 1,8-naphthyridine | `c1cnc2ncccc2c1` | 16 | 162 | 25 | not in the catalogue: the network has not seen it | yes |
| 5-fluoroindole | `Fc1ccc2[nH]ccc2c1` | 16 | 162 | 25 | in the catalogue (B_d6f7e7dcae) but not among the molecules the network trained on | yes |
| azulene | `c1ccc2cccc-2cc1` | 18 | 166 | 27 | in the catalogue (A_d9139359ab) but not among the molecules the network trained on | yes |
| phenol | `Oc1ccccc1` | 13 | 117 | 9 | in the network's training set (B_3db4fe6829): the hold-out error is not this molecule's measure | no |
| benzonitrile | `N#Cc1ccccc1` | 13 | 130 | 12 | in the network's training set (B_3100da3761) and also in hold-out (a) as A_3100da3761: that hold-out was not clean for it, and the hold-out error is not this molecule's measure | no |
| phenylacetylene | `C#Cc1ccccc1` | 14 | 132 | 13 | in the network's training set (A_a848c04a21): the hold-out error is not this molecule's measure | no |
| styrene | `C=Cc1ccccc1` | 16 | 136 | 14 | in the network's training set (A_8f6ed7c002): the hold-out error is not this molecule's measure | no |
| indole | `c1ccc2[nH]ccc2c1` | 16 | 149 | 19 | in the network's training set (A_76e053ce6a): the hold-out error is not this molecule's measure | no |
| indene | `C1=Cc2ccccc2C1` | 17 | 151 | 20 | in the network's training set (A_90df3e4aa9): the hold-out error is not this molecule's measure | no |
| quinoline | `c1ccc2ncccc2c1` | 17 | 164 | 26 | in the network's training set (A_ff98e1160d): the hold-out error is not this molecule's measure | no |
| isoquinoline | `c1ccc2cnccc2c1` | 17 | 164 | 26 | in the network's training set (A_d09f8d1ef8): the hold-out error is not this molecule's measure | no |
| 4-fluoroquinoline | `Fc1ccnc2ccccc12` | 17 | 177 | 34 | in the catalogue (B_367feebe78) but not among the molecules the network trained on | no |
| 1-fluoronaphthalene | `Fc1cccc2ccccc12` | 18 | 179 | 35 | in the network's training set (B_96f5f1990a): the hold-out error is not this molecule's measure | no |
| 2-fluoronaphthalene | `Fc1ccc2ccccc2c1` | 18 | 179 | 35 | in the network's training set (B_14ba9f1827): the hold-out error is not this molecule's measure | no |
| 8-hydroxyquinoline | `Oc1cccc2cccnc12` | 18 | 179 | 35 | in the network's training set (B_02b3315726): the hold-out error is not this molecule's measure | no |
| 4-hydroxyquinoline | `Oc1ccnc2ccccc12` | 18 | 179 | 35 | in the network's training set (B_0399263529): the hold-out error is not this molecule's measure | no |
| 1-naphthol | `Oc1cccc2ccccc12` | 19 | 181 | 36 | in the network's training set (A_466972291d): the hold-out error is not this molecule's measure | no |
| 2-naphthol | `Oc1ccc2ccccc2c1` | 19 | 181 | 36 | in the catalogue (B_884132846f) but not among the molecules the network trained on | no |
| 1-naphthylamine | `Nc1cccc2ccccc12` | 20 | 183 | 37 | in the network's training set (B_89ae0e3368): the hold-out error is not this molecule's measure | no |
| 1-chloronaphthalene | `Clc1cccc2ccccc12` | 18 | 183 | 37 | in the network's training set (B_16116c90de): the hold-out error is not this molecule's measure | no |
| 2-methylquinoline | `Cc1ccc2ccccc2n1` | 20 | 183 | 37 | in the catalogue (B_d9cda76011) but not among the molecules the network trained on | no |
| 1-methylnaphthalene | `Cc1cccc2ccccc12` | 21 | 185 | 39 | in the network's training set (A_ea73419366): the hold-out error is not this molecule's measure | no |
| 2-methylnaphthalene | `Cc1ccc2ccccc2c1` | 21 | 185 | 39 | in the network's training set (A_69789470db): the hold-out error is not this molecule's measure | no |
| biphenylene | `c1ccc2c(c1)-c1ccccc1-2` | 20 | 196 | 47 | held out, hold-out (a) (A_72b86c2331): never trained on; the measured error includes it | no |
| acenaphthylene | `C1=Cc2cccc3cccc1c23` | 20 | 196 | 47 | in the network's training set (A_45187bb7c8): the hold-out error is not this molecule's measure | no |
