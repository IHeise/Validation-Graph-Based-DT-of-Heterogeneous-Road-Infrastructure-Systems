from ExperimentI_GraphSizes.Modul2_Evaluation.Performance import *
from ExperimentI_GraphSizes.Modul2_Evaluation.rev1.main_SoS import *
from ExperimentI_GraphSizes.Modul2_Evaluation.rev1.main_mono import *

# repeats anpassen!!!


#df = run_scalability(Mono_3_Querying_all_in_one_rev1,[1,2,3,4])
#df.to_csv("scalability_results_rev1_mono_all_in_one_3.2.csv", index=False)

print("-----------------FERTIG I-----------------")

df = run_scalability(Mono_4_Querying_all_in_one_rev1,[1,2,3,4])
df.to_csv("scalability_results_rev1_mono_all_in_one_4.2.csv", index=False)

df = run_scalability(Mono_4_Querying_rev1,[1,2,3,4,5])
df.to_csv("scalability_results_rev1_mono4.2.csv", index=False)

df = run_scalability(Mono_3_Querying_rev1,[1,2,3,4,5])
df.to_csv("scalability_results_rev1_mono3.2.csv", index=False)

df = run_scalability(SoS_4_Querying_rev1,[1,2,3,4,5])
df.to_csv("scalability_results_rev1_only4.2.csv", index=False)

print("-----------------FERTIG-----------------")

#df = run_scalability(SoS_5_Querying_rev1, [5])
#df.to_csv("scalability_results_rev1_only5.csv", index=False)

