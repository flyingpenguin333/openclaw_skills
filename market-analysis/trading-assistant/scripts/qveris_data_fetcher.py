# QVeris 数据获取模块
# 替换 AKShare，解决网络限制问题

import os
import json
import subprocess
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QVerisDataFetcher:
    """
    基于 QVeris 的股票数据获取器
    使用同花顺 iFinD 和 EODHD 数据源
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('QVERIS_API_KEY')
        if not self.api_key:
            raise ValueError("QVERIS_API_KEY not set")
        
        self.tool_path = os.path.expanduser("~/.openclaw/skills/qveris/scripts/qveris_tool.mjs")
        
        # 缓存搜索结果
        self._search_cache = {}
        
    def _run_command(self, command, timeout: int = 30) -> Dict:
        """
        运行 QVeris CLI 命令
        """
        try:
            env = os.environ.copy()
            env['QVERIS_API_KEY'] = self.api_key
            env['PYTHONIOENCODING'] = 'utf-8'
            
            # 支持字符串或列表命令
            if isinstance(command, list):
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='ignore',
                    timeout=timeout,
                    env=env
                )
            else:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='ignore',
                    timeout=timeout,
                    env=env
                )
            
            if result.returncode != 0:
                logger.error(f"QVeris command failed: {result.stderr}")
                return {'success': False, 'error': result.stderr}
            
            # 解析输出
            output = result.stdout
            
            # 尝试提取 JSON 结果 (查找 "Result:" 之后的 JSON)
            try:
                # 首先尝试找 "Result:" 标记
                result_marker = output.find('Result:')
                if result_marker != -1:
                    json_str = output[result_marker + 7:].strip()
                    return {'success': True, 'data': json.loads(json_str)}
                
                # 然后尝试找第一个 {
                json_start = output.find('{')
                if json_start != -1:
                    json_str = output[json_start:]
                    # 尝试解析
                    parsed = json.loads(json_str)
                    if 'data' in parsed or 'tools' in parsed:
                        return {'success': True, **parsed}
                    return {'success': True, 'data': parsed}
            except json.JSONDecodeError as e:
                logger.debug(f"JSON parse error: {e}, output: {output[:200]}")
                pass
            
            return {'success': True, 'raw_output': output}
            
        except subprocess.TimeoutExpired:
            logger.error("QVeris command timeout")
            return {'success': False, 'error': 'timeout'}
        except Exception as e:
            logger.error(f"QVeris command error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _parse_search_output(self, output: str) -> Dict:
        """
        解析 QVeris search 命令的文本输出
        """
        lines = output.strip().split('\n')
        
        search_id = None
        tools = []
        current_tool = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 提取 Search ID
            if line.startswith('Search ID:'):
                search_id = line.replace('Search ID:', '').strip()
                continue
            
            # 新工具开始 ([1], [2], etc.)
            if line.startswith('[') and ']' in line:
                if current_tool:
                    tools.append(current_tool)
                current_tool = {
                    'index': line.split(']')[0][1:],
                    'name': line.split(']')[1].strip() if ']' in line else '',
                    'id': None,
                    'success_rate': None,
                    'avg_time': None,
                    'required_params': [],
                    'optional_params': [],
                    'example': None
                }
                continue
            
            # 提取工具 ID
            if line.startswith('ID:') and current_tool:
                current_tool['id'] = line.replace('ID:', '').strip()
                continue
            
            # 提取成功率
            if 'Success:' in line and current_tool:
                try:
                    success_part = line.split('Success:')[1].split('|')[0].strip()
                    current_tool['success_rate'] = success_part
                except:
                    pass
                continue
            
            # 提取平均时间
            if 'Avg Time:' in line and current_tool:
                try:
                    time_part = line.split('Avg Time:')[1].strip()
                    current_tool['avg_time'] = time_part
                except:
                    pass
                continue
            
            # 提取必需参数
            if line.startswith('Required:') and current_tool:
                params = line.replace('Required:', '').strip()
                current_tool['required_params'] = [p.strip() for p in params.split(',') if p.strip()]
                continue
            
            # 提取可选参数
            if line.startswith('Optional:') and current_tool:
                params = line.replace('Optional:', '').strip()
                current_tool['optional_params'] = [p.strip() for p in params.split(',') if p.strip()]
                continue
            
            # 提取示例
            if line.startswith('Example:') and current_tool:
                try:
                    example = line.replace('Example:', '').strip()
                    current_tool['example'] = json.loads(example)
                except:
                    current_tool['example'] = line.replace('Example:', '').strip()
                continue
        
        # 添加最后一个工具
        if current_tool:
            tools.append(current_tool)
        
        return {
            'search_id': search_id,
            'tools': tools,
            'count': len(tools)
        }
    
    def search_tools(self, query: str, limit: int = 10) -> Dict:
        """
        搜索 QVeris 工具
        
        Args:
            query: 搜索关键词，如 "China A-share stock price"
            limit: 返回结果数量
            
        Returns:
            包含 search_id 和 tools 的字典
        """
        cache_key = f"{query}_{limit}"
        if cache_key in self._search_cache:
            return self._search_cache[cache_key]
        
        cmd = ['node', self.tool_path, 'search', query, '--limit', str(limit)]
        result = self._run_command(cmd)
        
        if not result.get('success', False):
            logger.error(f"Search failed: {result.get('error')}")
            return {'search_id': None, 'tools': [], 'count': 0}
        
        # 解析文本输出
        parsed = self._parse_search_output(result.get('raw_output', ''))
        
        # 缓存结果
        self._search_cache[cache_key] = parsed
        return parsed
    
    def _parse_execute_output(self, output: str) -> Dict:
        """
        解析 QVeris execute 命令的文本输出
        """
        lines = output.strip().split('\n')
        
        result_data = None
        success = False
        time_ms = 0
        cost = 0
        
        in_result = False
        result_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检查是否成功
            if line.startswith('Success'):
                success = True
                continue
            
            # 提取时间和成本
            if 'Time:' in line and 'Cost:' in line:
                try:
                    time_part = line.split('Time:')[1].split('|')[0].strip()
                    time_ms = float(time_part.replace('ms', ''))
                    
                    cost_part = line.split('Cost:')[1].strip()
                    cost = float(cost_part)
                except:
                    pass
                continue
            
            # 开始收集 Result
            if line == 'Result:':
                in_result = True
                continue
            
            # 收集 Result 内容
            if in_result:
                result_lines.append(line)
        
        # 解析 Result JSON
        if result_lines:
            try:
                result_json = '\n'.join(result_lines)
                result_data = json.loads(result_json)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse result JSON: {e}")
                result_data = {'raw': '\n'.join(result_lines)}
        
        return {
            'success': success,
            'time_ms': time_ms,
            'cost': cost,
            'data': result_data
        }
    
    def execute_tool(self, tool_id: str, search_id: str, params: Dict) -> Dict:
        """
        执行 QVeris 工具
        
        Args:
            tool_id: 工具 ID
            search_id: 搜索 ID
            params: 工具参数
            
        Returns:
            执行结果
        """
        params_str = json.dumps(params)
        cmd = [
            'node', self.tool_path, 'execute', tool_id,
            '--search-id', search_id,
            '--params', params_str
        ]
        
        result = self._run_command(cmd, timeout=60)
        
        if not result.get('success', False):
            return result
        
        # 解析文本输出
        parsed = self._parse_execute_output(result.get('raw_output', ''))
        return parsed
    
    # ==================== 股票行情 ====================
    
    def get_realtime_quote_a_share(self, symbols: List[str]) -> List[Dict]:
        """
        获取A股实时行情
        
        Args:
            symbols: 股票代码列表，如 ['000001.SZ', '600519.SH']
            
        Returns:
            股票行情列表
        """
        try:
            # 搜索工具
            search_result = self.search_tools("China A-share stock real-time quotation", limit=5)
            
            if not search_result or not search_result.get('tools'):
                logger.error("No tools found")
                return []
            
            # 查找同花顺实时行情工具
            ths_tool = None
            for tool in search_result['tools']:
                if 'ths_ifind.real_time_quotation' in tool.get('id', ''):
                    ths_tool = tool
                    break
            
            if not ths_tool:
                logger.error("THS real-time quotation tool not found")
                return []
            
            logger.info(f"Found THS tool: {ths_tool['id']}")
            
            # 执行工具
            codes = ','.join(symbols)
            result = self.execute_tool(
                tool_id=ths_tool['id'],
                search_id=search_result['search_id'],
                params={'codes': codes}
            )
            
            if not result.get('success', False):
                logger.error(f"Execute tool failed: {result.get('error')}")
                return []
            
            # 解析数据
            response_data = result.get('data', {})
            if isinstance(response_data, dict) and 'data' in response_data:
                stock_arrays = response_data['data']
                if isinstance(stock_arrays, list) and len(stock_arrays) > 0:
                    stocks = []
                    for stock_list in stock_arrays:
                        if isinstance(stock_list, list):
                            for stock in stock_list:
                                stocks.append(self._normalize_ths_stock_data(stock))
                    return stocks
            elif isinstance(response_data, list):
                # 直接是数组格式
                stocks = []
                for stock_list in response_data:
                    if isinstance(stock_list, list):
                        for stock in stock_list:
                            stocks.append(self._normalize_ths_stock_data(stock))
                return stocks
            
            logger.warning(f"Unexpected data format: {type(response_data)}")
            return []
            
        except Exception as e:
            logger.error(f"Get A-share quote failed: {e}")
            return []
    
    def get_realtime_quote_us(self, symbols: List[str]) -> List[Dict]:
        """
        获取美股实时行情
        
        Args:
            symbols: 美股代码列表，如 ['AAPL', 'NVDA']
            
        Returns:
            股票行情列表
        """
        try:
            # 搜索工具
            search_result = self.search_tools("US stock price real-time", limit=5)
            
            if not search_result or not search_result.get('tools'):
                return []
            
            # 查找 EODHD 工具
            eod_tool = None
            for tool in search_result['tools']:
                if 'eodhd.live_prices' in tool.get('id', ''):
                    eod_tool = tool
                    break
            
            if not eod_tool:
                logger.error("EODHD live prices tool not found")
                return []
            
            logger.info(f"Found EODHD tool: {eod_tool['id']}")
            
            # 执行工具 (一次获取一个股票)
            stocks = []
            for symbol in symbols:
                ticker = f"{symbol}.US"
                result = self.execute_tool(
                    tool_id=eod_tool['id'],
                    search_id=search_result['search_id'],
                    params={'ticker': ticker}
                )
                
                if result.get('success', False):
                    stock_data = self._normalize_eodhd_stock_data(result.get('data', ''))
                    if stock_data:
                        stocks.append(stock_data)
            
            return stocks
            
        except Exception as e:
            logger.error(f"Get US stock quote failed: {e}")
            return []
    
    def get_realtime_quote(self, symbol: str, market: str = 'A') -> Optional[Dict]:
        """
        获取单只股票实时行情
        
        Args:
            symbol: 股票代码
            market: 市场，'A'-A股, 'US'-美股, 'HK'-港股
            
        Returns:
            股票行情
        """
        if market == 'A':
            # 添加后缀
            if symbol.startswith('6'):
                symbol = f"{symbol}.SH"
            else:
                symbol = f"{symbol}.SZ"
            
            results = self.get_realtime_quote_a_share([symbol])
        elif market == 'US':
            results = self.get_realtime_quote_us([symbol])
        else:
            # 港股暂未实现
            return None
        
        return results[0] if results else None
    
    # ==================== 板块数据 ====================
    
    def get_sector_list(self) -> List[Dict]:
        """
        获取板块列表
        
        Returns:
            板块列表
        """
        try:
            search_result = self.search_tools("China stock sector industry classification", limit=5)
            
            if not search_result:
                return []
            
            # TODO: 实现板块列表获取
            return []
            
        except Exception as e:
            logger.error(f"Get sector list failed: {e}")
            return []
    
    def get_sector_hot(self, top_n: int = 5) -> List[Dict]:
        """
        获取热点板块
        
        Args:
            top_n: 返回前几名
            
        Returns:
            热点板块列表
        """
        try:
            search_result = self.search_tools("China A-share sector fund flow ranking hot", limit=5)
            
            if not search_result:
                return []
            
            # 查找板块资金流向工具
            tools = search_result.get('tools', [])
            fund_flow_tool = None
            for tool in tools:
                if 'sector' in tool.get('id', '').lower() and 'fund' in tool.get('id', '').lower():
                    fund_flow_tool = tool
                    break
            
            if not fund_flow_tool:
                # 使用 A股实时行情，按行业分组统计
                return self._calculate_sector_hot_from_stocks(top_n)
            
            # 执行工具
            result = self.execute_tool(
                tool_id=fund_flow_tool['id'],
                search_id=search_result.get('search_id', ''),
                params={'limit': top_n}
            )
            
            # 解析结果
            data = result.get('data', [])
            return data[:top_n] if isinstance(data, list) else []
            
        except Exception as e:
            logger.error(f"Get sector hot failed: {e}")
            return []
    
    def _calculate_sector_hot_from_stocks(self, top_n: int = 5) -> List[Dict]:
        """
        从个股行情计算板块热度 (备用方案)
        """
        # 获取一些代表性股票
        sample_symbols = [
            '000001.SZ',  # 银行
            '600519.SH',  # 白酒
            '000858.SZ',  # 食品饮料
            '601398.SH',  # 银行
            '600036.SH',  # 银行
        ]
        
        stocks = self.get_realtime_quote_a_share(sample_symbols)
        
        # 简单分类统计
        sectors = {}
        for stock in stocks:
            sector = stock.get('sector', '其他')
            if sector not in sectors:
                sectors[sector] = {'count': 0, 'total_change': 0}
            
            sectors[sector]['count'] += 1
            sectors[sector]['total_change'] += stock.get('change_pct', 0)
        
        # 计算平均涨跌幅
        result = []
        for sector, data in sectors.items():
            avg_change = data['total_change'] / data['count'] if data['count'] > 0 else 0
            result.append({
                'sector_name': sector,
                'change_pct': avg_change,
                'hot_score': abs(avg_change) * 10  # 简单热度评分
            })
        
        result.sort(key=lambda x: abs(x['change_pct']), reverse=True)
        return result[:top_n]
    
    # ==================== 历史数据 ====================
    
    def get_hist_kline(self, symbol: str, market: str = 'A', 
                       period: str = 'daily', days: int = 30) -> List[Dict]:
        """
        获取历史K线数据
        
        Args:
            symbol: 股票代码
            market: 市场
            period: 周期，daily/weekly/monthly
            days: 获取多少天的数据
            
        Returns:
            K线数据列表
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            search_result = self.search_tools("stock historical price data API", limit=5)
            
            if not search_result:
                return []
            
            # TODO: 实现历史数据获取
            # 目前 QVeris 搜索到的工具可能不包含完整的历史数据API
            # 需要进一步测试
            
            return []
            
        except Exception as e:
            logger.error(f"Get hist kline failed: {e}")
            return []
    
    # ==================== 新闻数据 ====================
    
    def get_stock_news(self, symbol: str, num: int = 10) -> List[Dict]:
        """
        获取个股新闻
        
        Args:
            symbol: 股票代码
            num: 新闻数量
            
        Returns:
            新闻列表
        """
        try:
            search_result = self.search_tools("stock news API financial", limit=5)
            
            if not search_result:
                return []
            
            # TODO: 实现新闻获取
            # 需要找到合适的 QVeris 新闻工具
            
            return []
            
        except Exception as e:
            logger.error(f"Get stock news failed: {e}")
            return []
    
    # ==================== 数据标准化 ====================
    
    def _normalize_ths_stock_data(self, data: Dict) -> Dict:
        """
        标准化同花顺股票数据
        """
        return {
            'symbol': data.get('thscode', '').replace('.SZ', '').replace('.SH', ''),
            'name': data.get('name', ''),
            'market': 'A股',
            'price': data.get('latest', 0),
            'pre_close': data.get('preClose', 0),
            'open': data.get('open', 0),
            'high': data.get('high', 0),
            'low': data.get('low', 0),
            'change': data.get('change', 0),
            'change_pct': data.get('changeRatio', 0),
            'volume': data.get('volume', 0),
            'amount': data.get('amount', 0),
            'turnover': data.get('turnoverRatio', 0),
            'pe': data.get('pe_ttm', 0),
            'pb': data.get('pbr_lf', 0),
            'sector': self._infer_sector(data),
            'time': data.get('time', ''),
        }
    
    def _normalize_eodhd_stock_data(self, data) -> Optional[Dict]:
        """
        标准化 EODHD 股票数据
        """
        try:
            # 处理不同的数据格式
            if isinstance(data, dict):
                # 已经是字典格式
                data_dict = data
            elif isinstance(data, str):
                # CSV 格式
                lines = data.strip().split('\n')
                if len(lines) < 2:
                    return None
                
                header = lines[0].split(',')
                values = lines[1].split(',')
                data_dict = dict(zip(header, values))
            else:
                return None
            
            return {
                'symbol': data_dict.get('code', '').replace('.US', ''),
                'name': '',  # EODHD 不返回名称
                'market': '美股',
                'price': float(data_dict.get('close', 0)),
                'pre_close': float(data_dict.get('previousClose', 0)),
                'open': float(data_dict.get('open', 0)),
                'high': float(data_dict.get('high', 0)),
                'low': float(data_dict.get('low', 0)),
                'change': float(data_dict.get('change', 0)),
                'change_pct': float(data_dict.get('change_p', 0)),
                'volume': int(float(data_dict.get('volume', 0))),
                'amount': 0,  # EODHD 不返回成交额
                'turnover': 0,
                'pe': 0,
                'pb': 0,
                'sector': '',
                'time': datetime.fromtimestamp(int(float(data_dict.get('timestamp', 0)))).strftime('%Y-%m-%d %H:%M:%S') if data_dict.get('timestamp') else '',
            }
        except Exception as e:
            logger.error(f"Normalize EODHD data failed: {e}, data type: {type(data)}")
            return None
    
    def _infer_sector(self, data: Dict) -> str:
        """
        从数据推断行业 (简化版)
        """
        # 可以根据股票代码或PE/PB等特征推断
        # 这里使用简化逻辑
        symbol = data.get('thscode', '')
        
        # 根据常见股票代码判断
        if symbol in ['000001.SZ', '601398.SH', '600036.SH']:
            return '银行'
        elif symbol in ['600519.SH', '000858.SZ']:
            return '白酒'
        
        return '其他'


# ==================== 测试代码 ====================

if __name__ == "__main__":
    import os
    
    # 测试
    api_key = os.getenv('QVERIS_API_KEY')
    if not api_key:
        print("请先设置 QVERIS_API_KEY")
        exit(1)
    
    fetcher = QVerisDataFetcher(api_key)
    
    print("=" * 60)
    print("QVeris 股票数据获取测试")
    print("=" * 60)
    
    # 测试1: A股实时行情
    print("\n【测试1】平安银行 + 贵州茅台")
    stocks = fetcher.get_realtime_quote_a_share(['000001.SZ', '600519.SH'])
    for stock in stocks:
        print(f"  {stock['name']}: ¥{stock['price']} ({stock['change_pct']:+.2f}%)")
    
    # 测试2: 美股实时行情
    print("\n【测试2】苹果 + 英伟达")
    us_stocks = fetcher.get_realtime_quote_us(['AAPL', 'NVDA'])
    for stock in us_stocks:
        print(f"  {stock['symbol']}: ${stock['price']} ({stock['change_pct']:+.2f}%)")
    
    # 测试3: 热点板块
    print("\n【测试3】热点板块 (计算得出)")
    sectors = fetcher.get_sector_hot(top_n=5)
    for sector in sectors:
        print(f"  {sector['sector_name']}: {sector['change_pct']:+.2f}%")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
