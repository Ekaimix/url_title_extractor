import urllib.request
import urllib.error
import urllib.parse
import concurrent.futures
import argparse
import csv
import sys
import re
from urllib.parse import urlparse

def get_title(url):
    """获取指定URL的网站标题"""
    # 确保URL有协议前缀
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req, timeout=10)
        
        # 获取响应内容
        charset = response.headers.get_content_charset()
        if not charset:
            charset = 'utf-8'  # 默认使用utf-8编码
        
        html = response.read().decode(charset, errors='replace')
        
        # 使用正则表达式提取标题
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else "无标题"
        
        # 获取网站域名
        domain = urlparse(url).netloc
        
        return {
            'url': url,
            'title': title,
            'domain': domain,
            'status': 'success',
            'status_code': response.status
        }
    except urllib.error.HTTPError as e:
        return {
            'url': url,
            'title': '获取失败',
            'domain': urlparse(url).netloc if '//' in url else '',
            'status': 'error',
            'status_code': e.code,
            'error': str(e)
        }
    except urllib.error.URLError as e:
        return {
            'url': url,
            'title': '获取失败',
            'domain': urlparse(url).netloc if '//' in url else '',
            'status': 'error',
            'status_code': 'N/A',
            'error': str(e.reason)
        }
    except Exception as e:
        return {
            'url': url,
            'title': '获取失败',
            'domain': urlparse(url).netloc if '//' in url else '',
            'status': 'error',
            'error': str(e)
        }

def process_urls(urls, max_workers=10):
    """并行处理多个URL，保持原始顺序"""
    results = [None] * len(urls)
    url_to_index = {url: i for i, url in enumerate(urls)}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(get_title, url): url for url in urls}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            result = future.result()
            index = url_to_index[url]
            results[index] = result
            print(f"处理: {result['url']} - {'✓' if result['status'] == 'success' else '✗'} - {result['title']}")
    
    return results

def read_urls_from_file(file_path):
    """从文件中读取URL列表"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def save_to_csv(results, output_file):
    """将结果保存到CSV文件"""
    fieldnames = ['url', 'title', 'domain', 'status', 'status_code', 'error']
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow({k: v for k, v in result.items() if k in fieldnames})

def main():
    parser = argparse.ArgumentParser(description='批量获取URL的网站标题')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-u', '--url', help='单个URL')
    group.add_argument('-f', '--file', help='包含URL列表的文件路径')
    parser.add_argument('-o', '--output', help='输出CSV文件路径', default='url_titles.csv')
    parser.add_argument('-w', '--workers', type=int, help='并行处理的线程数', default=10)
    
    args = parser.parse_args()
    
    if args.url:
        urls = [args.url]
    else:
        try:
            urls = read_urls_from_file(args.file)
        except Exception as e:
            print(f"读取文件失败: {e}")
            sys.exit(1)
    
    print(f"开始处理 {len(urls)} 个URL...")
    results = process_urls(urls, args.workers)
    
    # 统计成功和失败的数量
    success_count = sum(1 for r in results if r['status'] == 'success')
    error_count = len(results) - success_count
    
    print(f"\n处理完成! 成功: {success_count}, 失败: {error_count}")
    
    save_to_csv(results, args.output)
    print(f"结果已保存到 {args.output}")

if __name__ == "__main__":
    main()