const BASE_URL = "https://qveris.ai/api/v1";

async function executeTool(toolId, searchId, parameters, maxResponseSize = 20480, timeoutMs = 120000) {
  const apiKey = process.env.QVERIS_API_KEY;
  if (!apiKey) {
    console.error("Error: QVERIS_API_KEY environment variable not set");
    process.exit(1);
  }
  
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const url = new URL(`${BASE_URL}/tools/execute`);
    url.searchParams.set("tool_id", toolId);

    const response = await fetch(url.toString(), {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        search_id: searchId,
        parameters,
        max_response_size: maxResponseSize,
      }),
      signal: controller.signal,
    });

    if (!response.ok) {
      const text = await response.text();
      console.error(`HTTP Error: ${response.status}`);
      console.error(text);
      process.exit(1);
    }

    return await response.json();
  } finally {
    clearTimeout(timeout);
  }
}

async function main() {
  const result = await executeTool(
    "ths_ifind.real_time_quotation.v1",
    "eca63e33-9a1e-4921-b252-6aeb697800e6",
    { codes: "000001.SZ,600519.SH" }
  );
  
  // Parse and format the stock prices
  if (result.status === "success" && result.data) {
    const data = result.data;
    const timestamp = new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' });
    
    console.log("\n=== A股实时行情 ===");
    console.log(`时间: ${timestamp}\n`);
    
    // Parse the quotation data
    if (data.quotation && Array.isArray(data.quotation)) {
      data.quotation.forEach(stock => {
        const changePct = stock.p_change ? stock.p_change.toFixed(2) : 'N/A';
        const changeSymbol = stock.p_change > 0 ? '+' : '';
        console.log(`${stock.name} (${stock.code})`);
        console.log(`  当前价: ${stock.now_price || 'N/A'}`);
        console.log(`  涨跌: ${changeSymbol}${changePct}%`);
        console.log(`  最高: ${stock.high || 'N/A'} | 最低: ${stock.low || 'N/A'}`);
        console.log(`  开盘价: ${stock.open || 'N/A'} | 昨收: ${stock.yesterday_price || 'N/A'}`);
        console.log('---');
      });
    } else {
      console.log("原始数据:", JSON.stringify(data, null, 2));
    }
  } else {
    console.error("获取数据失败:", result.error || result.message || "Unknown error");
    console.log("完整响应:", JSON.stringify(result, null, 2));
  }
}

main().catch(e => {
  console.error(`Error: ${e.message}`);
  process.exit(1);
});
