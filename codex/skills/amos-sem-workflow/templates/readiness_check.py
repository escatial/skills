"""
AMOS 达标预检验 —— 一键跑完进 AMOS 前的所有关卡

用法：
    pip install pandas numpy scipy pyreadstat factor-analyzer
    python readiness_check.py

输出一份「能不能进 AMOS」的判定报告。

任何一关 FAIL → 先修数据/修量表，不要进 AMOS。
"""

import sys
import numpy as np
import pandas as pd
from scipy import stats

# Windows 中文控制台默认 GBK，会在输出 D²、α 等字符时崩溃
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ==================== 配置区 ====================
DATA_FILE = r"D:\data\survey.sav"      # 支持 .sav / .csv / .xlsx

# 维度 → 题项
SCALES = {
    "F1": ["A1", "A2", "A3", "A4"],
    "F2": ["B1", "B2", "B3", "B4"],
    "F3": ["C1", "C2", "C3"],
}

REVERSE_ITEMS = []        # 反向题，如 ["A3", "B2"]
LIKERT_MAX, LIKERT_MIN = 5, 1
N_PARAMS = 30             # 模型待估参数个数（用于 N:p 比）
# ===============================================

RESULT = []

def check(name, passed, detail):
    RESULT.append((name, passed, detail))
    print(f"[{'PASS' if passed else 'FAIL'}] {name}\n       {detail}\n")


def load(path):
    if path.lower().endswith(".sav"):
        import pyreadstat
        df, _ = pyreadstat.read_sav(path)
        return df
    if path.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(path)
    return pd.read_csv(path)


def cronbach_alpha(X):
    X = X.dropna()
    k = X.shape[1]
    if k < 2:
        return np.nan
    return k / (k - 1) * (1 - X.var(ddof=1).sum() / X.sum(axis=1).var(ddof=1))


def kmo_bartlett(M):
    """KMO 取样适切性 + Bartlett 球形检验（纯 numpy/scipy，无需 factor-analyzer）"""
    n, p = M.shape
    R = np.corrcoef(M.T)

    # Bartlett：chi2 = -[(n-1) - (2p+5)/6] * ln|R|
    sign, logdet = np.linalg.slogdet(R)
    chi2 = -((n - 1) - (2 * p + 5) / 6) * logdet
    dfree = p * (p - 1) / 2
    p_val = 1 - stats.chi2.cdf(chi2, dfree)

    # KMO：偏相关矩阵由 R 的逆导出
    R_inv = np.linalg.pinv(R)
    d = np.sqrt(np.diag(R_inv))
    partial = -R_inv / np.outer(d, d)     # 偏相关（含符号）
    np.fill_diagonal(partial, 0)
    Rc = R.copy()
    np.fill_diagonal(Rc, 0)

    ss_r = np.sum(Rc ** 2)
    ss_p = np.sum(partial ** 2)
    kmo = ss_r / (ss_r + ss_p)
    return kmo, chi2, p_val, int(dfree)


def main():
    df = load(DATA_FILE)
    items = [i for v in SCALES.values() for i in v]

    # ---------- 0. 反向计分 ----------
    if REVERSE_ITEMS:
        df[REVERSE_ITEMS] = (LIKERT_MAX + LIKERT_MIN) - df[REVERSE_ITEMS]
        print(f"已对 {len(REVERSE_ITEMS)} 个反向题重新计分\n")

    X = df[items]

    # ---------- 1. 样本量 ----------
    n = len(X.dropna())
    ratio = n / N_PARAMS
    check("样本量 (N ≥ 200, N:p ≥ 5:1)",
          n >= 200 and ratio >= 5,
          f"N = {n}, 待估参数 = {N_PARAMS}, N:p = {ratio:.1f}:1")

    # ---------- 2. 缺失 ----------
    miss = X.isna().mean()
    check("缺失值 (< 5%)",
          miss.max() < .05,
          f"最大缺失率 = {miss.max():.1%} （题项：{miss.idxmax()}）")

    # ---------- 3. 正态性 ----------
    sk, ku = X.skew(), X.kurtosis()   # pandas 给的是超额峰度
    bad = ((sk.abs() > 3) | (ku.abs() > 8))
    check("正态性 (|偏度|<3, |峰度|<8)",
          not bad.any(),
          f"偏度 [{sk.min():.2f}, {sk.max():.2f}], 峰度 [{ku.min():.2f}, {ku.max():.2f}]"
          + (f"\n       ⚠️ 超标题项：{list(bad[bad].index)} → 改用 Bootstrap ML" if bad.any() else ""))

    # ---------- 4. 多变量异常值 ----------
    Xc = X.dropna()
    mu = Xc.mean().values
    S_inv = np.linalg.pinv(np.cov(Xc.values.T))
    d2 = np.array([(r - mu) @ S_inv @ (r - mu) for r in Xc.values])
    p_mah = 1 - stats.chi2.cdf(d2, df=Xc.shape[1])
    n_out = int((p_mah < .001).sum())
    check("多变量异常值 (Mahalanobis D², p<.001)",
          n_out / len(Xc) < .05,
          f"检出 {n_out} 个 ({n_out/len(Xc):.1%})")

    # ---------- 5. 共同方法偏差（Harman 单因子）----------
    R = np.corrcoef(Xc.values.T)
    eigvals = np.sort(np.linalg.eigvalsh(R))[::-1]
    var1 = eigvals[0] / len(eigvals)
    check("共同方法偏差 (Harman 第一因子 < 40%)",
          var1 < .40,
          f"第一因子解释方差 = {var1:.1%}")

    # ---------- 6. 信度 ----------
    alphas = {k: cronbach_alpha(df[v]) for k, v in SCALES.items()}
    check("信度 (Cronbach's α ≥ .70)",
          all(a >= .70 for a in alphas.values()),
          " | ".join(f"{k}: α={a:.3f}" for k, a in alphas.items()))

    # ---------- 7. KMO & Bartlett ----------
    kmo, chi2_b, p_bart, df_b = kmo_bartlett(Xc.values)
    check("EFA 适合性 (KMO ≥ .70, Bartlett p < .001)",
          kmo >= .70 and p_bart < .001,
          f"KMO = {kmo:.3f}, Bartlett χ²({df_b}) = {chi2_b:.1f}, p = {p_bart:.2e}")

    # ---------- 8. 因子间相关（共线性初筛）----------
    scores = pd.DataFrame({k: df[v].mean(axis=1) for k, v in SCALES.items()})
    corr = scores.corr()
    hi = (corr.abs() > .85) & (corr.abs() < 1)
    check("因子间相关 (< .85)",
          not hi.any().any(),
          f"最大相关 = {corr.where(corr < 1).abs().max().max():.3f}")

    # ---------- 汇总 ----------
    print("=" * 60)
    passed = sum(1 for _, p, _ in RESULT if p)
    total = len(RESULT)
    print(f"结果：{passed}/{total} 项通过")
    fails = [n for n, p, _ in RESULT if not p]
    if fails:
        print("\n❌ 未通过：")
        for f in fails:
            print(f"   · {f}")
        print("\n👉 先修数据 / 修量表，不要进 AMOS。")
        print("   进了 AMOS 再用修正指数救，只会得到一个无法复现的模型。")
    else:
        print("\n✅ 全部通过，可以进 AMOS 做 CFA。")
        print("   下一步：CFA 之后再算 CR / AVE / 区分效度（需要标准化载荷）。")
    print("=" * 60)


if __name__ == "__main__":
    main()
