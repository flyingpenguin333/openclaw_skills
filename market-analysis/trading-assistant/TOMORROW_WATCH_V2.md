# 明日关注综合分析系统 v2.0

**问题**: 原来的"明日关注"只是简单判断涨跌，缺乏深度分析  
**解决**: 构建多维度评分系统，综合技术面、资金面、估值面

---

## 🎯 新系统核心特性

### 五大分析维度

| 维度 | 权重 | 评分标准 | 说明 |
|------|------|----------|------|
| **价格动量** | 30% | 涨跌幅度 | 强势股识别 |
| **成交量** | 25% | 量比 | 资金关注度 |
| **资金流向** | 20% | 买卖盘比例 | 主力意图 |
| **技术形态** | 15% | 突破/支撑 | 技术信号 |
| **估值安全** | 10% | PE/PB | 安全边际 |

**总分**: 100分

---

## 📊 评分细则

### 1. 价格动量 (0-30分)

```python
if change_pct > 5:    score += 30  # 强势上涨
elif change_pct > 3:  score += 25  # 明显上涨
elif change_pct > 1:  score += 15  # 温和上涨
elif change_pct > 0:  score += 5   # 微涨
elif change_pct < -3: score += 10  # 超跌反弹潜力
```

**信号示例**:
- "Strong momentum: +5.2%"
- "Oversold bounce potential: -4.1%"

---

### 2. 成交量分析 (0-25分)

```python
if vol_ratio > 3:     score += 25  # 放量3倍以上
elif vol_ratio > 2:   score += 20  # 放量2倍以上
elif vol_ratio > 1.5: score += 10  # 明显放量
```

**信号示例**:
- "Volume spike: 3.2x average"
- "High volume: 2.1x average"

---

### 3. 资金流向 (0-20分)

```python
buy_ratio = buyVolume / (buyVolume + sellVolume)
if buy_ratio > 0.7:   score += 20  # 强烈买盘
elif buy_ratio > 0.6: score += 15  # 买盘占优
elif buy_ratio > 0.55: score += 10 # 买盘略多
```

**信号示例**:
- "Strong buying: 72% buy orders"
- "Institutional accumulation detected"

---

### 4. 技术形态 (0-15分)

```python
if price >= high * 0.998:  score += 15  # 突破日内高点
if rise_days >= 3:         score += 10  # 连涨3天以上
if price <= low * 1.002:   score += 5   # 回踩支撑
```

**信号示例**:
- "Breakout: New intraday high"
- "Support bounce: Held key level"
- "Momentum continuation: 3-day streak"

---

### 5. 估值安全 (0-10分)

```python
if 0 < pe < 15:  score += 10  # 低估值
if 0 < pb < 1:   score += 10  # 破净
if pe < 25:      score += 5   # 合理估值
```

**信号示例**:
- "Attractive valuation: PE 8.5x"
- "Below book value: PB 0.85x"

---

## 🏷️ 优先级分类

根据总分将股票分为三类：

### 🔥 HIGH PRIORITY (Score >= 50)
**特征**: 
- 强势上涨 + 放量 + 资金流入
- 技术突破 + 估值合理

**操作建议**:
- 次日开盘考虑建仓
- 止损位: 今日最低价
- 目标收益: 3-5%

---

### 📊 MEDIUM PRIORITY (Score 30-49)
**特征**:
- 有1-2个积极信号
- 但不够强势

**操作建议**:
- 观察开盘30分钟
- 等待更明确信号
- 小仓位试探

---

### 👀 WATCH LIST (Score < 30)
**特征**:
- 信号较弱
- 或只有单一维度

**操作建议**:
- 放入观察池
- 等待催化事件
- 不急于操作

---

## 📝 示例输出

```
================================================================
TOMORROW'S WATCHLIST
================================================================

HIGH PRIORITY (Score >= 50)
----------------------------------------------------------------

1. 比亚迪 (002594)
   Score: 65/100 [HIGH PRIORITY]
   Signals:
      ✓ Strong momentum: +3.2%
      ✓ Volume spike: 2.5x average
      ✓ Strong buying: 68% buy orders
      ✓ Breakout: New intraday high
      ✓ Sector hot: New energy
   Why Watch: 
      Strong sector momentum + volume confirmation + technical breakout
   Suggestion:
      - Entry: If opens above today's close
      - Stop loss: Today's low
      - Target: 5-8% gain

MEDIUM PRIORITY (Score 30-49)
----------------------------------------------------------------

2. 平安银行 (000001)
   Score: 40/100 [MEDIUM PRIORITY]
   Signals:
      • Oversold bounce potential: -0.55%
      • Attractive valuation: PE 4.8x
      • High dividend yield
   Why Watch:
      Low valuation + oversold, potential rebound
   Suggestion:
      - Wait for volume confirmation
      - Entry: If breaks 10.80 resistance

3. 贵州茅台 (600519)
   Score: 35/100 [MEDIUM PRIORITY]
   Signals:
      • Defensive stock
      • Stable performance: -0.36%
      • Core asset status
   Why Watch:
      Defensive play in volatile market

================================================================
TRADING SUGGESTIONS
================================================================

1. Market Context:
   - Check overnight US market performance
   - Watch for policy/news catalysts
   - Monitor sector rotation

2. Risk Management:
   - Max position per stock: 20%
   - Stop loss: 3-5% from entry
   - Take profit: 5-10% target

3. Execution Strategy:
   - HIGH PRIORITY: Consider market open entry
   - MEDIUM PRIORITY: Wait for 30-min confirmation
   - All positions: Set stop loss immediately

================================================================
Disclaimer: This analysis is for reference only.
================================================================
```

---

## 🔄 实现代码

### 核心分析函数
```python
def calculate_watch_score(data: Dict) -> int:
    """计算明日关注评分"""
    score = 0
    
    # 1. 价格动量 (0-30)
    change_pct = data.get('changeRatio', 0)
    if change_pct > 5: score += 30
    elif change_pct > 3: score += 25
    elif change_pct > 1: score += 15
    
    # 2. 成交量 (0-25)
    vol_ratio = data.get('vol_ratio', 0)
    if vol_ratio > 3: score += 25
    elif vol_ratio > 2: score += 20
    
    # 3. 资金流向 (0-20)
    buy_ratio = data.get('buyVolume', 0) / (data.get('buyVolume', 0) + data.get('sellVolume', 0))
    if buy_ratio > 0.7: score += 20
    elif buy_ratio > 0.6: score += 15
    
    # 4. 技术形态 (0-15)
    if data.get('latest', 0) >= data.get('high', 0) * 0.998: score += 15
    
    # 5. 估值安全 (0-10)
    pe = data.get('pe_ttm', 0)
    if 0 < pe < 15: score += 10
    
    return min(score, 100)
```

---

## 🚀 下一步优化

### 可以添加的分析维度

1. **消息面分析**
   - 个股新闻情感分析
   - 公告类型识别（利好/利空）
   - 研报评级变化

2. **板块联动**
   - 行业龙头带动效应
   - 上下游产业链联动
   - 概念热点映射

3. **市场情绪**
   - 涨跌停家数比
   - 北向资金流向
   - 融资融券余额

4. **基本面催化**
   - 业绩预增公告
   - 重大合同签订
   - 股权变动

5. **技术指标**
   - MACD金叉/死叉
   - RSI超买超卖
   - 布林带突破

---

## ✅ 总结

新系统相比原版的改进：

| 对比项 | 原版 | 新版 |
|--------|------|------|
| 分析维度 | 单一（价格） | 5维度综合 |
| 评分系统 | 无 | 0-100分 |
| 优先级 | 无 | 高/中/低三档 |
| 操作建议 | 无 | 具体买卖建议 |
| 风险考虑 | 无 | 估值安全垫 |

**新版优势**:
- ✅ 更全面的分析
- ✅ 量化评分系统
- ✅ 清晰的优先级
- ✅ 可操作的建议

---

**已更新文件**: `scripts/tomorrow_watch_advanced.py`
