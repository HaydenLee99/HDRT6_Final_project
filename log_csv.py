import pandas as pd

log_act = pd.read_csv("data/flat_action_log.csv")
log_bul = pd.read_csv("data/flat_bullet_log.csv")

# time 컬럼 통일
log_act["time"] = log_act["time"].astype(float)
log_bul["time"] = log_bul["time"].astype(float)

# 단순 concat 후 정렬 (진짜 "그냥 합치기")
merged = pd.concat([log_act, log_bul], ignore_index=True)

# time 기준 정렬
merged = merged.sort_values("time").reset_index(drop=True)

merged.to_csv("data/merged_log.csv", index=False)