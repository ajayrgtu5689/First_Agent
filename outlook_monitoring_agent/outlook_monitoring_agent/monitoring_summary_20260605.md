# 📊 Friday Monitoring Summary (05-Jun-2026)

## 1. 🗄️ Tablespace Status

### 🔴 High Utilization (Critical/Watch)

* None ✅

### 🟡 Moderate Utilization (85–90%)

* None ✅

### ✅ Stable

* 6 tablespaces below 85% — all within healthy limits

## 2. 💽 Diskgroup (ASM) Status

> No diskgroup data available.


## 3. 💾 PROD Mount Point Status

### 🔴 High Usage Filesystems

* `/dev/xvdf1` → **91% used**
* `/dev/nvme4n1p1` → **85% used**
* `/dev/xvdf1` → **85% used**
* `/dev/xvdf1` → **84% used**
* `/dev/xvdf1` → **84% used**
* `/dev/nvme4n1p1` → **84% used**
* `/dev/xvdf1` → **84% used**
* `/dev/xvdd1` → **84% used**
* `/dev/nvme4n1p1` → **84% used**
* `/dev/xvdd1` → **83% used**
* `/dev/nvme1n1p1` → **83% used**
* `/dev/xvdf1` → **82% used**
* `/dev/nvme1n1p1` → **82% used**
* `/dev/xvdd1` → **82% used**
* `/dev/nvme1n1p1` → **82% used**

### 🟡 Moderate

* `/dev/nvme1n1p1` → ~77%
* `/dev/nvme1n1p1` → ~77%
* `/dev/nvme1n1p1` → ~77%
* `/dev/xvdx1` → ~76%
* `/dev/xvdx1` → ~76%
* `/dev/xvdx1` → ~76%
* `/dev/xvdx1` → ~76%
* `/dev/xvdx1` → ~76%
* `/dev/xvdx1` → ~76%
* `/dev/xvda1` → ~74%
* `/dev/xvda1` → ~74%
* `/dev/xvda1` → ~74%
* `/dev/xvdf1` → ~73%
* `/dev/xvdf1` → ~73%
* `/dev/xvdf1` → ~72%
* `/a01/EBSPRD/app/R12.2/fs_ne/EBSapps/xxsec/out` → ~71%
* `/a01/EBSPRD/app/R12.2/fs_ne/EBSapps/xxsec/in` → ~71%
* `/dev/nvme1n1p1` → ~71%
* `/dev/nvme4n1p1` → ~70%
* `/dev/nvme2n1p1` → ~70%
* `/dev/nvme4n1p1` → ~70%
* `/a01/EBSPRD/app/R12.2/fs_ne/EBSapps/xxsec/out` → ~70%
* `/a01/EBSPRD/app/R12.2/fs_ne/EBSapps/xxsec/in` → ~70%
* `/dev/nvme1n1p1` → ~70%
* `/dev/nvme2n1p1` → ~70%
* `/dev/nvme4n1p1` → ~70%
* `/a01/EBSPRD/app/R12.2/fs_ne/EBSapps/xxsec/out` → ~70%
* `/a01/EBSPRD/app/R12.2/fs_ne/EBSapps/xxsec/in` → ~70%
* `/dev/nvme1n1p1` → ~70%
* `/dev/nvme0n1p2` → ~67%
* `/dev/xvdf1` → ~67%
* `/dev/nvme0n1p2` → ~67%
* `/dev/nvme0n1p2` → ~67%
* `/dev/xvdf1` → ~67%
* `/dev/nvme0n1p2` → ~67%
* `/dev/nvme0n1p2` → ~67%
* `/dev/xvdf1` → ~67%
* `/dev/nvme0n1p2` → ~67%
* `/dev/nvme0n1p2` → ~66%
* `/dev/xvde1` → ~66%
* `/dev/nvme0n1p2` → ~66%
* `/dev/xvde1` → ~66%
* `/dev/nvme0n1p2` → ~66%
* `/dev/nvme3n1p1` → ~66%
* `/dev/xvde1` → ~66%
* `/dev/nvme5n1p1` → ~65%
* `/dev/nvme5n1p1` → ~65%
* `/dev/nvme5n1p1` → ~65%
* `/dev/nvme5n1p1` → ~65%
* `/dev/nvme5n1p1` → ~65%
* `/dev/nvme5n1p1` → ~65%

### ✅ Healthy

* `/dev/xvda1`, `/dev/xvdo1`, `/dev/xvdg1`, `/dev/nvme0n1p1`, `/dev/nvme3n1p1`, `/dev/nvme2n1p1` → low usage

👉 **Observation:**

* `/dev/xvdf1` filesystem needs monitoring
* No filesystem is critically full yet

# 🚨 Overall Key Alerts (Today)

* **`/dev/xvdf1` mount point (~82%) → Needs monitoring**
* **`/dev/nvme1n1p1` mount point (~82%) → Needs monitoring**
* **`/dev/xvdf1` mount point (~84%) → Needs monitoring**
* **`/dev/xvdd1` mount point (~82%) → Needs monitoring**
* **`/dev/nvme4n1p1` mount point (~85%) → Needs monitoring**
* **`/dev/xvdf1` mount point (~91%) → Needs monitoring**
* **`/dev/nvme1n1p1` mount point (~82%) → Needs monitoring**
* **`/dev/xvdf1` mount point (~84%) → Needs monitoring**
* **`/dev/xvdd1` mount point (~83%) → Needs monitoring**
* **`/dev/nvme4n1p1` mount point (~84%) → Needs monitoring**
* **`/dev/xvdf1` mount point (~85%) → Needs monitoring**
* **`/dev/nvme1n1p1` mount point (~83%) → Needs monitoring**
* **`/dev/xvdf1` mount point (~84%) → Needs monitoring**
* **`/dev/xvdd1` mount point (~84%) → Needs monitoring**
* **`/dev/nvme4n1p1` mount point (~84%) → Needs monitoring**

# ✅ Final Health Summary

* ✅ DEV/TST → Stable
* ✅ PROD → Healthy
