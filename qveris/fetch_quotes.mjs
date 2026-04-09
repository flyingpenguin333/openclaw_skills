const BASE_URL = "https://qveris.ai/api/v1";

async function executeTool(toolId, searchId, parameters) {
  const apiKey = process.env.QVERIS_API_KEY;
  if (!apiKey) {
    console.error("Error: QVERIS_API_KEY environment variable not set");
    process.exit(1);
  }

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
      max_response_size: 20480,
    }),
  });

  if (!response.ok) {
    const text = await response.text();
    console.error(`HTTP Error: ${response.status}`);
    console.error(text);
    process.exit(1);
  }

  return await response.json();
}

async function main() {
  const result = await executeTool(
    "ths_ifind.real_time_quotation.v1",
    "f82b5895-9cf2-4858-aa0e-e54d055c02c1",
    { codes: "000001.SZ,600519.SH" }
  );
  console.log(JSON.stringify(result, null, 2));
}

main().catch(e => {
  console.error(`Error: ${e.message}`);
  process.exit(1);
});
