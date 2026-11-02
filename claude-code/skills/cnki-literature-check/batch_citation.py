#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知网文献批量检索工具
用于批量获取文献的GB/T 7714-2015格式引文和摘要

使用方法:
    python batch_citation.py --input titles.txt --output results.md
    
或直接在代码中修改文献列表后运行
"""

import asyncio
import json
import re
import time
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ArticleInfo:
    """文献信息数据类"""
    title: str
    authors: str
    journal: str
    year: str
    volume: str
    pages: str
    doi: str
    abstract: str
    keywords: str
    
    def to_gb7714(self, index: int = 1) -> str:
        """生成GB/T 7714-2015格式引文"""
        return f"[{index}] {self.authors}. {self.title}[J]. {self.journal}, {self.year}, {self.volume}: {self.pages}."
    
    def to_markdown(self, index: int = 1) -> str:
        """生成Markdown格式输出"""
        return f"""---
## [{index}] {self.title}

**作者：** {self.authors}
**期刊/来源：** {self.journal}
**年份：** {self.year}
**卷(期)：** {self.volume}
**页码：** {self.pages}
**DOI：** {self.doi}

### GB/T 7714-2015 引文
{self.to_gb7714(index)}

### 摘要
{self.abstract}

**关键词：** {self.keywords}
"""


class CNKIScraper:
    """知网文献检索器"""
    
    def __init__(self):
        self.base_url = "https://kns.cnki.net"
        self.search_url = f"{self.base_url}/kns8s/defaultresult/index"
        self.results: List[ArticleInfo] = []
        self.failed_titles: List[str] = []
    
    async def search_article(self, title: str, browser_page) -> Optional[ArticleInfo]:
        """
        检索单篇文献
        
        Args:
            title: 文献标题
            browser_page: Playwright页面对象
            
        Returns:
            ArticleInfo对象或None
        """
        try:
            # 1. 访问搜索页面
            await browser_page.goto(self.search_url)
            await asyncio.sleep(2)
            
            # 2. 输入搜索词
            await browser_page.locator('#txt_search').fill(title)
            await asyncio.sleep(1)
            
            # 3. 触发搜索
            await browser_page.evaluate("""
                () => {
                    const searchBtn = document.querySelector('.search-btn');
                    if (searchBtn) {
                        const clickEvent = new MouseEvent('click', { bubbles: true });
                        searchBtn.dispatchEvent(clickEvent);
                    }
                }
            """)
            await asyncio.sleep(3)
            
            # 4. 查找文献链接
            article_url = await browser_page.evaluate("""
                (title) => {
                    const allElements = document.querySelectorAll('*');
                    for (let el of allElements) {
                        if (el.children.length === 0 && el.textContent.trim() === title) {
                            let parent = el.parentElement;
                            while (parent && parent.tagName !== 'A') {
                                parent = parent.parentElement;
                            }
                            if (parent) return parent.href;
                        }
                    }
                    return null;
                }
            """, title)
            
            if not article_url:
                print(f"  [!] {title[:50]}...")
                self.failed_titles.append(title)
                return None
            
            # 5. 访问文献详情页
            await browser_page.goto(article_url)
            await asyncio.sleep(3)
            
            # 6. 提取信息
            info = await browser_page.evaluate("""
                () => {
                    const bodyText = document.body.innerText;
                    
                    // 提取摘要
                    const abstractMatch = bodyText.match(/摘要[：:]\\s*([\\s\\S]*?)(?=关键词|Key words|中图分类号|文献标识码|$)/i);
                    
                    // 提取关键词
                    const keywordsMatch = bodyText.match(/关键词[：:]\\s*([\\s\\S]*?)(?=中图分类号|文献标识码|基金资助|$)/i);
                    
                    // 提取DOI
                    const doiMatch = bodyText.match(/DOI[：:]\\s*(10\\.[^\\s]+)/i);
                    
                    // 提取年份
                    const yearMatch = bodyText.match(/(20\\d{2})\\s*年/);
                    
                    // 提取卷期
                    const volumeMatch = bodyText.match(/(\\d+)\\s*\\(\\s*(\\d+)\\s*\\)/);
                    
                    // 提取页码
                    const pagesMatch = bodyText.match(/(\\d+[-+]\\d+)/);
                    
                    return {
                        abstract: abstractMatch ? abstractMatch[1].trim() : '',
                        keywords: keywordsMatch ? keywordsMatch[1].trim() : '',
                        doi: doiMatch ? doiMatch[1] : '',
                        year: yearMatch ? yearMatch[1] : '',
                        volume: volumeMatch ? volumeMatch[0] : '',
                        pages: pagesMatch ? pagesMatch[1] : ''
                    };
                }
            """)
            
            # 7. 构建ArticleInfo对象
            # 注意：作者和期刊名需要从页面其他位置提取
            article = ArticleInfo(
                title=title,
                authors="待补充",  # 需要从页面提取
                journal="待补充",  # 需要从页面提取
                year=info.get('year', ''),
                volume=info.get('volume', ''),
                pages=info.get('pages', ''),
                doi=info.get('doi', ''),
                abstract=info.get('abstract', ''),
                keywords=info.get('keywords', '')
            )
            
            print(f"  [OK] {title[:50]}...")
            return article
            
        except Exception as e:
            print(f"  [X] [{title[:50]}...]: {str(e)}")
            self.failed_titles.append(title)
            return None
    
    async def batch_search(self, titles: List[str], delay: int = 3) -> List[ArticleInfo]:
        """
        批量检索文献
        
        Args:
            titles: 文献标题列表
            delay: 每篇文献检索间隔（秒）
            
        Returns:
            ArticleInfo列表
        """
        from playwright.async_api import async_playwright
        
        print(f"开始批量检索，共 {len(titles)} 篇文献...")
        print("=" * 60)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            for i, title in enumerate(titles, 1):
                print(f"\n[{i}/{len(titles)}] 正在检索: {title}")
                
                article = await self.search_article(title, page)
                if article:
                    self.results.append(article)
                
                if i < len(titles):
                    print(f"  等待 {delay} 秒后继续...")
                    await asyncio.sleep(delay)
            
            await browser.close()
        
        print("\n" + "=" * 60)
        print(f"检索完成！成功: {len(self.results)} 篇，失败: {len(self.failed_titles)} 篇")
        
        return self.results
    
    def save_to_markdown(self, filepath: str):
        """保存结果为Markdown文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("# 文献检索结果\n\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"共检索文献: {len(self.results)} 篇\n\n")
            
            for i, article in enumerate(self.results, 1):
                f.write(article.to_markdown(i))
                f.write("\n\n")
            
            if self.failed_titles:
                f.write("---\n\n")
                f.write("## 检索失败的文献\n\n")
                for title in self.failed_titles:
                    f.write(f"- {title}\n")
        
        print(f"\n结果已保存至: {filepath}")
    
    def save_to_json(self, filepath: str):
        """保存结果为JSON文件"""
        data = {
            "generated_time": datetime.now().isoformat(),
            "total": len(self.results),
            "articles": [
                {
                    "title": a.title,
                    "authors": a.authors,
                    "journal": a.journal,
                    "year": a.year,
                    "volume": a.volume,
                    "pages": a.pages,
                    "doi": a.doi,
                    "abstract": a.abstract,
                    "keywords": a.keywords,
                    "citation": a.to_gb7714(i+1)
                }
                for i, a in enumerate(self.results)
            ],
            "failed": self.failed_titles
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"JSON数据已保存至: {filepath}")


# 使用示例
if __name__ == "__main__":
    # 示例文献列表
    sample_titles = [
        "基于TOC及启发式规则的生产计划与控制方法",
    ]
    
    async def main():
        scraper = CNKIScraper()
        
        # 批量检索
        await scraper.batch_search(sample_titles, delay=3)
        
        # 保存结果
        scraper.save_to_markdown("文献检索结果.md")
        scraper.save_to_json("文献检索结果.json")
    
    # 运行
    asyncio.run(main())
