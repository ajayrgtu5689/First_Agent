# 📊 Wednesday Monitoring Summary (10-Jun-2026)

## 1. 🗄️ Tablespace Status

| Database | Tablespace | Used % | Status |
|----------|------------|:------:|--------|
| CDBPRD | TS_CDB_DATA | 93.0% | 🔴 Critical |
| HFATST | TS_BULK_DATA | 92.2% | 🔴 Critical |
| CTSPRD | TS_REPLICATION | 92.0% | 🔴 Critical |
| CTSDEV | USERS | 90.9% | 🔴 Critical |
| EBSTST | APPS_TS_XXSEC | 89.0% | 🟡 Warning |
| HFAPRD | TS_HFA_DATA | 88.9% | 🟡 Warning |
| HFATST | GG_USER | 88.9% | 🟡 Warning |
| CTSTST | TS_BULK_DATA | 88.4% | 🟡 Warning |
| CTSPRD | TS_ESONG_DATA | 88.3% | 🟡 Warning |
| EBSDEV | APPS_TS_XXSEC | 88.0% | 🟡 Warning |
| CDBPRD | TS_REPLICATION | 87.5% | 🟡 Warning |
| CTSTST | TS_APEX | 87.1% | 🟡 Warning |
| HFATST | TS_REPLICATION | 86.7% | 🟡 Warning |
| HFAPRD | TS_REPLICATION | 86.0% | 🟡 Warning |
| HFADEV | TS_REPLICATION | 86.0% | 🟡 Warning |
| CTSTST | TS_GG_USER | 85.9% | 🟡 Warning |
| REPTST | T_SOAINFRA | 85.6% | 🟡 Warning |
| CDBPRD | TS_GG_USER | 85.5% | 🟡 Warning |
| EBSPRD | SYSTEM | 83.0% | ✅ Stable |
| EBSTST | SYSTEM | 83.0% | ✅ Stable |
| EBSDEV | SYSTEM | 83.0% | ✅ Stable |
| EBSQTS | SYSTEM | 83.0% | ✅ Stable |

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

| Host | Mount Point | Used % | Status |
|------|-------------|:------:|--------|
| CDBPRD | `/u01` | 84% | 🔴 Critical |
| CTSPRD | `/a01` | 82% | 🔴 Critical |
| EBSPRD | `/a01` | 82% | 🔴 Critical |
| HFAPRD | `/u01` | 82% | 🔴 Critical |
| EBSPRD | `/xxsec_out` | 71% | 🟡 Warning |
| EBSPRD | `/xxsec_in` | 71% | 🟡 Warning |
| EBSPRD | `/d12` | 70% | 🟡 Warning |
| EBSPRD | `/` | 67% | 🟡 Warning |
| EBSPRD | `/d02` | 65% | 🟡 Warning |
| CDBPRD | `/` | 58% | ✅ Stable |
| REPPRD | `/a01` | 57% | ✅ Stable |
| EBSPRD | `/d03` | 53% | ✅ Stable |
| HFAPRD | `/` | 51% | ✅ Stable |
| CDBPRD | `/d99` | 47% | ✅ Stable |
| REPPRD | `/d03` | 44% | ✅ Stable |
| EBSPRD | `/boot` | 43% | ✅ Stable |
| REPPRD | `/d02` | 38% | ✅ Stable |
| CTSPRD | `/` | 37% | ✅ Stable |
| CDBPRD | `/d11` | 35% | ✅ Stable |
| CDBPRD | `/u02` | 29% | ✅ Stable |
| CDBPRD | `/d03` | 28% | ✅ Stable |
| EBSPRD | `/d01` | 22% | ✅ Stable |
| CTSPRD | `/d03` | 19% | ✅ Stable |
| REPPRD | `/d01` | 18% | ✅ Stable |
| REPPRD | `/` | 15% | ✅ Stable |
| CTSPRD | `/u02` | 6% | ✅ Stable |
| HFAPRD | `/u02` | 4% | ✅ Stable |
| EBSPRD | `/run` | 2% | ✅ Stable |
| CTSPRD | `/dev/shm` | 1% | ✅ Stable |
| CTSPRD | `/EFS` | 1% | ✅ Stable |
| CTSPRD | `/FTP01` | 1% | ✅ Stable |
| CTSPRD | `/cts` | 1% | ✅ Stable |
| CTSPRD | `/cts01` | 1% | ✅ Stable |
| EBSPRD | `/dev/shm` | 1% | ✅ Stable |
| EBSPRD | `/EFS` | 1% | ✅ Stable |
| EBSPRD | `/run/user/42` | 1% | ✅ Stable |
| EBSPRD | `/run/user/55331` | 1% | ✅ Stable |
| EBSPRD | `/FTP01/Chase` | 1% | ✅ Stable |
| EBSPRD | `/FTP01/anaplan` | 1% | ✅ Stable |
| EBSPRD | `/FTP01/floqast` | 1% | ✅ Stable |
| EBSPRD | `/run/user/55333` | 1% | ✅ Stable |
| REPPRD | `/EFS` | 1% | ✅ Stable |
| CDBPRD | `/dev/shm` | 1% | ✅ Stable |
| CDBPRD | `/d01` | 1% | ✅ Stable |
| CDBPRD | `/d33` | 1% | ✅ Stable |
| CDBPRD | `/EFS` | 1% | ✅ Stable |
| CDBPRD | `/FTP01` | 1% | ✅ Stable |
| HFAPRD | `/dev/shm` | 1% | ✅ Stable |
| HFAPRD | `/EFS` | 1% | ✅ Stable |
| HFAPRD | `/FTP01` | 1% | ✅ Stable |
| HFAPRD | `/hfa01` | 1% | ✅ Stable |
| HFAPRD | `/cts01` | 1% | ✅ Stable |
| HFAPRD | `/cts` | 1% | ✅ Stable |
| CTSPRD | `/win_cifs` | 0% | ✅ Stable |
| EBSPRD | `/dev` | 0% | ✅ Stable |
| EBSPRD | `/sys/fs/cgroup` | 0% | ✅ Stable |
| EBSPRD | `/run/user/800` | 0% | ✅ Stable |
| EBSPRD | `/run/user/0` | 0% | ✅ Stable |
| EBSPRD | `/win_cifs` | 0% | ✅ Stable |
| REPPRD | `/dev/shm` | 0% | ✅ Stable |

## 4. 💾 TST & DEV Mount Point Status

| Host | Mount Point | Used % | Status |
|------|-------------|:------:|--------|
| EBSDEV | `/a01` | 85% | 🔴 Critical |
| EBSTST | `/a01` | 77% | 🟡 Warning |
| HFADEV | `/hd02` | 76% | 🟡 Warning |
| CDBDEV | `/hd02` | 76% | 🟡 Warning |
| CTSTST | `/` | 74% | 🟡 Warning |
| REPTST | `/a01` | 73% | 🟡 Warning |
| EBSDEV | `/d12` | 70% | 🟡 Warning |
| CTSTST | `/a01` | 67% | 🟡 Warning |
| EBSDEV | `/` | 67% | 🟡 Warning |
| EBSTST | `/` | 66% | 🟡 Warning |
| HFATST | `/u02` | 66% | 🟡 Warning |
| EBSTST | `/d02` | 64% | ✅ Stable |
| EBSDEV | `/d02` | 64% | ✅ Stable |
| CTSDEV | `/` | 63% | ✅ Stable |
| CTSDEV | `/a01` | 63% | ✅ Stable |
| EBSDEV | `/xxsec_in` | 62% | ✅ Stable |
| EBSDEV | `/xxsec_out` | 62% | ✅ Stable |
| REPDEV | `/a01` | 60% | ✅ Stable |
| HFADEV | `/hd12` | 60% | ✅ Stable |
| HFADEV | `/hfa01` | 60% | ✅ Stable |
| CDBDEV | `/hd12` | 60% | ✅ Stable |
| CDBDEV | `/hfa01` | 60% | ✅ Stable |
| EBSTST | `/xxsec_in` | 58% | ✅ Stable |
| EBSTST | `/xxsec_out` | 58% | ✅ Stable |
| REPDEV | `/d03` | 58% | ✅ Stable |
| HFADEV | `/` | 55% | ✅ Stable |
| CDBDEV | `/` | 55% | ✅ Stable |
| HFATST | `/u01` | 53% | ✅ Stable |
| HFATST | `/` | 50% | ✅ Stable |
| EBSTST | `/d12` | 48% | ✅ Stable |
| REPTST | `/d03` | 47% | ✅ Stable |
| HFADEV | `/d22` | 46% | ✅ Stable |
| HFADEV | `/ha01` | 46% | ✅ Stable |
| CDBDEV | `/d22` | 46% | ✅ Stable |
| CDBDEV | `/ha01` | 46% | ✅ Stable |
| REPTST | `/d01` | 45% | ✅ Stable |
| EBSTST | `/boot` | 43% | ✅ Stable |
| EBSDEV | `/boot` | 43% | ✅ Stable |
| REPDEV | `/d02` | 41% | ✅ Stable |
| REPTST | `/d02` | 38% | ✅ Stable |
| HFADEV | `/a01` | 36% | ✅ Stable |
| CDBDEV | `/a01` | 36% | ✅ Stable |
| REPTST | `/` | 31% | ✅ Stable |
| HFADEV | `/d02` | 29% | ✅ Stable |
| CDBDEV | `/d02` | 29% | ✅ Stable |
| CTSTST | `/d03` | 23% | ✅ Stable |
| HFADEV | `/d12` | 23% | ✅ Stable |
| CDBDEV | `/d12` | 23% | ✅ Stable |
| CTSDEV | `/d03` | 18% | ✅ Stable |
| REPDEV | `/` | 15% | ✅ Stable |
| EBSTST | `/d01` | 14% | ✅ Stable |
| HFADEV | `/d01` | 10% | ✅ Stable |
| HFADEV | `/d03` | 10% | ✅ Stable |
| CDBDEV | `/d01` | 10% | ✅ Stable |
| CDBDEV | `/d03` | 10% | ✅ Stable |
| EBSTST | `/run` | 5% | ✅ Stable |
| EBSDEV | `/run` | 5% | ✅ Stable |
| CTSTST | `/u02` | 4% | ✅ Stable |
| EBSDEV | `/d01` | 4% | ✅ Stable |
| EBSDEV | `/dev/shm` | 3% | ✅ Stable |
| EBSDEV | `/d03` | 3% | ✅ Stable |
| REPDEV | `/d01` | 3% | ✅ Stable |
| EBSTST | `/dev/shm` | 2% | ✅ Stable |
| HFADEV | `/hd01` | 2% | ✅ Stable |
| CDBDEV | `/hd01` | 2% | ✅ Stable |
| CTSTST | `/dev/shm` | 1% | ✅ Stable |
| CTSTST | `/EFS` | 1% | ✅ Stable |
| CTSTST | `/FTP01` | 1% | ✅ Stable |
| CTSTST | `/cts` | 1% | ✅ Stable |
| CTSTST | `/cts01` | 1% | ✅ Stable |
| CTSDEV | `/dev/shm` | 1% | ✅ Stable |
| CTSDEV | `/d01` | 1% | ✅ Stable |
| CTSDEV | `/EFS` | 1% | ✅ Stable |
| CTSDEV | `/FTP01` | 1% | ✅ Stable |
| CTSDEV | `/cts01` | 1% | ✅ Stable |
| CTSDEV | `/cts` | 1% | ✅ Stable |
| EBSTST | `/d03` | 1% | ✅ Stable |
| EBSTST | `/EFS` | 1% | ✅ Stable |
| EBSTST | `/run/user/42` | 1% | ✅ Stable |
| EBSTST | `/run/user/55328` | 1% | ✅ Stable |
| EBSTST | `/FTP01/Chase` | 1% | ✅ Stable |
| EBSDEV | `/EFS` | 1% | ✅ Stable |
| EBSDEV | `/run/user/42` | 1% | ✅ Stable |
| EBSDEV | `/run/user/55325` | 1% | ✅ Stable |
| EBSDEV | `/FTP01/Chase` | 1% | ✅ Stable |
| EBSDEV | `/run/user/55327` | 1% | ✅ Stable |
| REPDEV | `/EFS` | 1% | ✅ Stable |
| REPTST | `/EFS` | 1% | ✅ Stable |
| HFATST | `/dev/shm` | 1% | ✅ Stable |
| HFATST | `/EFS` | 1% | ✅ Stable |
| HFATST | `/FTP01` | 1% | ✅ Stable |
| HFATST | `/cts` | 1% | ✅ Stable |
| HFATST | `/hfa01` | 1% | ✅ Stable |
| HFADEV | `/dev/shm` | 1% | ✅ Stable |
| HFADEV | `/hd03` | 1% | ✅ Stable |
| HFADEV | `/EFS` | 1% | ✅ Stable |
| HFADEV | `/FTP01` | 1% | ✅ Stable |
| HFADEV | `/cts` | 1% | ✅ Stable |
| HFADEV | `/cts01` | 1% | ✅ Stable |
| CDBDEV | `/dev/shm` | 1% | ✅ Stable |
| CDBDEV | `/hd03` | 1% | ✅ Stable |
| CDBDEV | `/EFS` | 1% | ✅ Stable |
| CDBDEV | `/FTP01` | 1% | ✅ Stable |
| CDBDEV | `/cts` | 1% | ✅ Stable |
| CDBDEV | `/cts01` | 1% | ✅ Stable |
| CTSDEV | `/win_cifs` | 0% | ✅ Stable |
| EBSTST | `/dev` | 0% | ✅ Stable |
| EBSTST | `/sys/fs/cgroup` | 0% | ✅ Stable |
| EBSTST | `/run/user/800` | 0% | ✅ Stable |
| EBSTST | `/run/user/55330` | 0% | ✅ Stable |
| EBSDEV | `/dev` | 0% | ✅ Stable |
| EBSDEV | `/sys/fs/cgroup` | 0% | ✅ Stable |
| EBSDEV | `/run/user/800` | 0% | ✅ Stable |
| EBSDEV | `/run/user/0` | 0% | ✅ Stable |
| REPDEV | `/dev/shm` | 0% | ✅ Stable |
| REPTST | `/dev/shm` | 0% | ✅ Stable |

# 🚨 Overall Key Alerts (Today)

| Resource | Type | Used % | Status |
|----------|------|:------:|--------|
| `CDBPRD DATA` | Diskgroup | 93% | 🔴 Critical |
| `CDBPRD TS_CDB_DATA` | Tablespace | 93% | 🔴 Critical |
| `HFATST TS_BULK_DATA` | Tablespace | 92% | 🔴 Critical |
| `CTSPRD TS_REPLICATION` | Tablespace | 92% | 🔴 Critical |
| `CTSDEV USERS` | Tablespace | 91% | 🔴 Critical |
| `/a01` | Mount Point | 85% | 🟠 Needs monitoring |
| `/u01` | Mount Point | 84% | 🟠 Needs monitoring |
| `/a01` | Mount Point | 82% | 🟠 Needs monitoring |
| `/a01` | Mount Point | 82% | 🟠 Needs monitoring |
| `/u01` | Mount Point | 82% | 🟠 Needs monitoring |

# ✅ Final Health Summary

| Environment | Status |
|-------------|--------|
| DEV / TST | ⚠️ Issues detected |
| PROD | ⚠️ Moderate risk areas exist |
| Critical focus | 🔴 CDBPRD (TS_CDB_DATA), CDBPRD storage, CTSDEV (USERS), CTSPRD (TS_REPLICATION), HFATST (TS_BULK_DATA) |
