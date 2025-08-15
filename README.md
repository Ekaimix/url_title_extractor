# URL标题批量提取工具

这是一个用Python编写的工具，可以批量处理URL并提取网站标题。

## 功能特点

- 支持批量处理多个URL
- 多线程并行处理，提高效率
- 自动处理URL格式（添加https://前缀）
- 结果导出为CSV格式
- 显示处理进度和统计信息

## 依赖库

使用前需要安装以下Python库：

```bash
pip install requests beautifulsoup4
```

## 使用方法

### 处理单个URL

```bash
python url_title_extractor.py -u https://www.example.com
```

### 处理URL列表文件

```bash
python url_title_extractor.py -f example_urls.txt
```

### 指定输出文件

```bash
python url_title_extractor.py -f example_urls.txt -o results.csv
```

### 设置并行线程数

```bash
python url_title_extractor.py -f example_urls.txt -w 20
```

## 参数说明

- `-u, --url`: 指定单个URL进行处理
- `-f, --file`: 指定包含URL列表的文件路径
- `-o, --output`: 指定输出CSV文件路径（默认为url_titles.csv）
- `-w, --workers`: 指定并行处理的线程数（默认为10）

## 输出格式

CSV文件包含以下字段：
- url: 处理的URL
- title: 网站标题
- domain: 网站域名
- status: 处理状态（success/error）
- status_code: HTTP状态码
- error: 错误信息（如果有）