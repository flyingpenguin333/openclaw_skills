---
name: browser
description: Browser automation using Puppeteer to render JavaScript-heavy web pages and extract dynamic content. Use when web_fetch cannot get the data because the page requires JavaScript execution (e.g., real-time stock prices, dynamic dashboards, Single Page Applications). Triggers on phrases like "render this page", "get dynamic content", "browser automation", "puppeteer", "JS rendered page", "headless browser".
---

# Browser Skill

This skill uses Puppeteer to launch a headless Chrome browser, render web pages (including JavaScript execution), and extract content.

## When to Use This Skill

Use this skill when:
- web_fetch returns empty or incomplete content
- The page requires JavaScript to load data (e.g., stock prices, dashboards)
- You need to interact with dynamic web applications
- Static HTML scraping is insufficient

## Usage

### Basic Page Reading

```bash
node index.js read <url>
```

Example:
```bash
node index.js read "https://stockpage.10jqka.com.cn/002594/"
```

### Output

The script returns the rendered page text content after JavaScript execution.

## Technical Details

- Uses Puppeteer to control headless Chrome
- Waits for network idle (networkidle2) before extracting content
- Executes all page JavaScript
- Returns clean text content from document.body.innerText

## Requirements

- Node.js
- Puppeteer (already installed in node_modules)

## Limitations

- Slower than web_fetch (requires browser startup)
- Higher resource usage
- Not suitable for high-frequency requests
- Some sites may block headless browsers
