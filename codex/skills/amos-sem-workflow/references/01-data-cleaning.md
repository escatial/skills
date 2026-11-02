# 数据清洗

> 顺序很重要：**反向计分 → 无效样本剔除 → 缺失值 → 异常值**。
> 顺序错了会出问题（例如：没做反向计分就算 α，α 会低得离谱）。

---

## 1. 反向计分（先做！）

反向题必须先转换，否则**信度、因子分析、SEM 全部错**。

5 点量表：`新值 = 6 − 原值`
7 点量表：`新值 = 8 − 原值`
（通式：`新值 = (最大值 + 最小值) − 原值`）

**SPSS**：`转换 → 重新编码为不同变量`，或
```
COMPUTE A3_R = 6 - A3.
EXECUTE.
```

**Python**：
```python
reverse_items = ["A3", "B2", "C5"]
df[reverse_items] = 6 - df[reverse_items]
```

> ✅ 自查：反向计分后，该题与同维度其他题的相关应**由负转正**。如果还是负的，说明这题根本不属于这个维度。

---

## 2. 无效样本剔除（事先定规则）

| 类型 | 判定 |
|---|---|
| **规律作答** | 连续 N 题选同一选项（如连续 10 题全选 3） |
| **作答时间过短** | 低于题量 × 2 秒（或低于中位数的 1/3） |
| **测谎题/注意力检测题** 答错 | 直接剔除 |
| **缺失过多** | 单份问卷缺失 > 20% |
| **方差为 0** | 该被试所有题项答案完全相同 |

**Python 检测规律作答**：
```python
# 标准差为 0 → 所有题选同一个
flat = df[items].std(axis=1) == 0

# 最长连续相同作答
def max_run(row):
    m = c = 1
    for i in range(1, len(row)):
        c = c + 1 if row[i] == row[i-1] else 1
        m = max(m, c)
    return m
df["max_run"] = df[items].apply(max_run, axis=1)
suspicious = df["max_run"] >= 10
```

> **规则必须事先定，并在论文中报告剔除了多少、为什么。**

---

## 3. 缺失值

### 先看比例和模式

```python
miss = df[items].isna().mean().sort_values(ascending=False)
print(miss[miss > 0])
```

| 缺失比例 | 处理 |
|---|---|
| < 5% | 均值替换 / EM / 直接删除，影响都不大 |
| 5–15% | **EM 算法** 或 **多重插补**（不要简单均值替换） |
| > 20%（某题） | 考虑删除该题 |
| > 20%（某人） | 删除该样本 |

### Little's MCAR 检验

判断缺失是否**完全随机**：
- **p > .05** → MCAR，可放心用简单方法处理
- **p < .05** → 不是完全随机，建议用 **EM / 多重插补 / FIML**

**SPSS**：`分析 → 缺失值分析` → 勾选 **EM** → 输出中含 Little's MCAR 检验

### FIML（AMOS 中处理缺失的推荐方式）

AMOS 支持全信息极大似然（FIML）：
`Analysis Properties → Estimation → ☑ Estimate means and intercepts`

> ⚠️ 用了 FIML 之后，AMOS **不再输出部分拟合指标**（如 GFI、AGFI、RMR）。
> 如果你需要完整拟合指标，就先插补，再跑模型。**事先想清楚。**

---

## 4. 异常值

### 单变量
标准化后 **|z| > 3.29**（对应 p < .001）

```python
from scipy import stats
z = np.abs(stats.zscore(df[items], nan_policy="omit"))
print("单变量异常值:", (z > 3.29).any(axis=1).sum())
```

### 多变量：Mahalanobis D²（SEM 必做）

**SPSS**：
1. `分析 → 回归 → 线性`
2. 因变量放**任意一个 ID 变量**（只是为了借用这个过程）
3. 自变量放**全部观测变量**
4. `保存 → 距离 → ☑ 马氏距离`
5. 计算 p 值：
```
COMPUTE p_mah = 1 - CDF.CHISQ(MAH_1, k).   /* k = 观测变量个数 */
EXECUTE.
```
6. **p < .001 → 多变量异常值**

**Python**：
```python
import numpy as np
from scipy import stats

X = df[items].dropna()
mu = X.mean().values
S_inv = np.linalg.inv(np.cov(X.values.T))
d2 = np.array([(r - mu) @ S_inv @ (r - mu) for r in X.values])
p = 1 - stats.chi2.cdf(d2, df=X.shape[1])
outliers = p < .001
print("多变量异常值:", outliers.sum())
```

### 处理原则

- **不要无脑删**。先核查：是录入错误？是规律作答？还是真实的极端个体？
- 删除必须**报告数量与理由**
- 删除比例 **> 5%** → 说明数据质量本身有问题，要反思收集过程
- 真实的极端值（不是错误）可以保留，或做敏感性分析（删与不删各跑一次，看结论是否稳健）

---

## 5. 清洗后的自查

- [ ] 反向题已转换，且与同维度题项相关为正
- [ ] 无效样本按事先定好的规则剔除，数量已记录
- [ ] 缺失比例、缺失机制（MCAR）已报告
- [ ] 多变量异常值已用 Mahalanobis D² 检查
- [ ] 最终样本量 N 已确定
- [ ] **每一步剔除了多少、为什么，全部有记录**（论文里要写）

---

## 输出：数据清洗记录表

| 步骤 | 剔除数 | 剩余 | 理由 |
|---|---|---|---|
| 原始回收 | — | 520 | |
| 规律作答 | 18 | 502 | 连续 ≥10 题同一选项 |
| 作答时间过短 | 12 | 490 | < 120 秒 |
| 缺失 > 20% | 7 | 483 | |
| 多变量异常（D², p<.001） | 9 | **474** | |

> 这张表直接可以写进论文的"数据收集与清洗"一节。
