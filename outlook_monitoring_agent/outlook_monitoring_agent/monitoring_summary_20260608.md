# 📊 Monday Monitoring Summary (08-Jun-2026)

## 1. 🗄️ Tablespace Status

| Database | Tablespace | Used % | Status |
|----------|------------|:------:|--------|
| APPS_ | TS_XXSEC | 60.0% | ✅ Stable |

## 2. 💽 Diskgroup (ASM) Status

| Database | Diskgroup | Used % | Status |
|----------|-----------|:------:|--------|
| CDBPRD | DATA | 93.1% | 🔴 Critical |
| HFATST | BULK | 87.8% | 🟡 Warning |
| CTSPRD | DATA | 78.8% | 🟡 Warning |
| CTSDEV | DATA | 73.1% | 🟡 Warning |
| CTSPRD | BULK | 71.1% | 🟡 Warning |
| CTSDEV | BULK | 66.1% | ✅ Stable |
| HFAPRD | DATA | 62.6% | ✅ Stable |
| HFAPRD | FRA | 62.3% | ✅ Stable |
| CTSTST | BULK | 57.2% | ✅ Stable |
| HFATST | DATA | 53.5% | ✅ Stable |
| HFAPRD | BULK | 52.4% | ✅ Stable |
| CTSPRD | FRA | 33.2% | ✅ Stable |
| CTSTST | DATA | 19.2% | ✅ Stable |
| CTSTST | FRA | 14.1% | ✅ Stable |
| HFATST | FRA | 9.7% | ✅ Stable |
| CTSDEV | FRA | 0.0% | ✅ Stable |

## 3. 💾 PROD Mount Point Status

| Mount Point | Used % | Status |
|-------------|:------:|--------|
| `/dev/nvme4n1p1` | 85% | 🔴 Critical |
| `/dev/xvdf1` | 84% | 🔴 Critical |
| `/dev/nvme1n1p1` | 82% | 🔴 Critical |
| `/dev/xvdd1` | 82% | 🔴 Critical |
| `/dev/xvdx1` | 76% | 🟡 Warning |
| `/dev/xvda1` | 74% | 🟡 Warning |
| `/a01/EBSPRD/app/R12.2/fs_ne/EBSapps/xxsec/out` | 71% | 🟡 Warning |
| `/a01/EBSPRD/app/R12.2/fs_ne/EBSapps/xxsec/in` | 71% | 🟡 Warning |
| `/dev/nvme2n1p1` | 70% | 🟡 Warning |
| `/dev/nvme0n1p2` | 67% | 🟡 Warning |
| `/dev/xvde1` | 66% | 🟡 Warning |
| `/dev/nvme5n1p1` | 65% | 🟡 Warning |
| `/dev/xvdc1` | 63% | ✅ Stable |
| `/dev/nvme3n1p1` | 63% | ✅ Stable |
| `/a01/EBSDEV/app/R12.2/fs_ne/EBSapps/xxsec/in` | 62% | ✅ Stable |
| `/a01/EBSDEV/app/R12.2/fs_ne/EBSapps/xxsec/out` | 62% | ✅ Stable |
| `/dev/xvdg1` | 60% | ✅ Stable |
| `/dev/xvds1` | 60% | ✅ Stable |
| `/dev/xvdw1` | 60% | ✅ Stable |
| `/a01/EBSTST/app/R12.2/fs_ne/EBSapps/xxsec/in` | 58% | ✅ Stable |
| `/a01/EBSTST/app/R12.2/fs_ne/EBSapps/xxsec/out` | 58% | ✅ Stable |
| `/dev/xvdk1` | 58% | ✅ Stable |
| `/dev/xvdp1` | 47% | ✅ Stable |
| `/dev/xvdq1` | 46% | ✅ Stable |
| `/dev/xvdt1` | 46% | ✅ Stable |
| `/dev/xvdi1` | 45% | ✅ Stable |
| `/dev/xvdj1` | 44% | ✅ Stable |
| `/dev/nvme0n1p1` | 43% | ✅ Stable |
| `/a01/EBSQTS/app/R12.2/fs_ne/EBSapps/xxsec/in` | 42% | ✅ Stable |
| `/a01/EBSQTS/app/R12.2/fs_ne/EBSapps/xxsec/out` | 42% | ✅ Stable |
| `/dev/xvdm1` | 38% | ✅ Stable |
| `/dev/xvdh1` | 35% | ✅ Stable |
| `/dev/xvdo1` | 23% | ✅ Stable |
| `/dev/xvdv1` | 4% | ✅ Stable |
| `/dev/xvdu1` | 2% | ✅ Stable |
| `/` | 1% | ✅ Stable |
| `/SESAC_Chase/Production` | 1% | ✅ Stable |
| `/anaplan` | 1% | ✅ Stable |
| `/floqast` | 1% | ✅ Stable |
| `/dev/xvdb1` | 1% | ✅ Stable |
| `/SESAC_Chase/Test` | 1% | ✅ Stable |

# 🚨 Overall Key Alerts (Today)

| Resource | Type | Used % | Status |
|----------|------|:------:|--------|
| `CDBPRD DATA` | Diskgroup | 93% | 🔴 Critical |
| `/dev/nvme4n1p1` | Mount Point | 85% | 🟠 Needs monitoring |
| `/dev/xvdf1` | Mount Point | 84% | 🟠 Needs monitoring |
| `/dev/nvme1n1p1` | Mount Point | 82% | 🟠 Needs monitoring |
| `/dev/xvdd1` | Mount Point | 82% | 🟠 Needs monitoring |

# ✅ Final Health Summary

| Environment | Status |
|-------------|--------|
| DEV / TST | ✅ Stable |
| PROD | ⚠️ Moderate risk areas exist |
| Critical focus | 🔴 CDBPRD storage |
