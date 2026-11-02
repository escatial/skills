#!/usr/bin/env node

/**
 * conf-papers: 学术论文搜索推荐
 * 支持中文核心期刊、中文硕士论文、英文期刊/顶会，覆盖所有学科领域
 */

const fs = require('fs');
const path = require('path');

// 工具函数
async function generateSearchQueries(query, paperType = '全部') {
  const queries = [];

  // 中文核心期刊搜索
  if (paperType === '全部' || paperType === '期刊') {
    queries.push({
      type: '中文核心期刊',
      query: `${query} 核心期刊 CSSCI site:cnki.net`,
      priority: 1
    });
    queries.push({
      type: '中文核心期刊',
      query: `${query} 期刊 site:cnki.net`,
      priority: 2
    });
  }

  // 中文硕士论文搜索
  if (paperType === '全部' || paperType === '硕士论文') {
    queries.push({
      type: '中文硕士论文',
      query: `${query} 硕士论文 site:cnki.net`,
      priority: 1
    });
    queries.push({
      type: '中文硕士论文',
      query: `${query} 学位论文 CNKI`,
      priority: 2
    });
  }

  // 英文期刊/顶会搜索
  if (paperType === '全部' || paperType === '顶会') {
    queries.push({
      type: '英文期刊/顶会',
      query: `${query} site:arxiv.org`,
      priority: 1
    });
    queries.push({
      type: '英文期刊/顶会',
      query: `${query} paper IEEE Springer`,
      priority: 2
    });
  }

  return queries;
}

function saveNote(paper, content) {
  const notesDir = path.join(process.cwd(), 'papers', 'notes');
  if (!fs.existsSync(notesDir)) {
    fs.mkdirSync(notesDir, { recursive: true });
  }

  const filename = (paper.title || 'untitled')
    .replace(/[^a-zA-Z0-9一-龥]/g, '_')
    .substring(0, 50);
  const filepath = path.join(notesDir, `${filename}.md`);

  fs.writeFileSync(filepath, content, 'utf-8');
  return filepath;
}

function formatOutput(queries) {
  let output = '## 搜索计划\n\n';
  output += '请使用 `mcp__MiniMax__web_search` 逐一搜索以下Query：\n\n';

  const grouped = {};
  for (const q of queries) {
    if (!grouped[q.type]) {
      grouped[q.type] = [];
    }
    grouped[q.type].push(q);
  }

  for (const [type, items] of Object.entries(grouped)) {
    output += `### ${type}\n`;
    items.forEach((item, i) => {
      output += `${i + 1}. ${item.query}\n`;
    });
    output += '\n';
  }

  output += '---\n\n';
  output += '## 搜索结果反馈模板\n\n';
  output += '```\n';
  output += '【论文标题】\n';
  output += '【作者】\n';
  output += '【来源/会议】\n';
  output += '【年份】\n';
  output += '【链接】\n';
  output += '【摘要】\n';
  output += '```\n\n';
  output += '请将搜索到的论文信息按上述格式整理，我将继续分析。';

  return output;
}

// 主函数
async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log('使用方法: node conf-papers.js <关键词> [文献类型]');
    console.log('');
    console.log('文献类型:');
    console.log('  期刊     - 仅搜索中文核心期刊');
    console.log('  硕士论文 - 仅搜索中文硕士论文');
    console.log('  顶会     - 仅搜索英文期刊/顶会');
    console.log('  全部     - 搜索所有类型（默认）');
    console.log('');
    console.log('示例:');
    console.log('  node conf-papers.js 水产品营销策略');
    console.log('  node conf-papers.js 企业战略 硕士论文');
    console.log('  node conf-papers.js 机器学习 顶会');
    process.exit(1);
  }

  const query = args[0];
  const typeMap = {
    '期刊': '期刊',
    '硕士论文': '硕士论文',
    '顶会': '顶会',
    '全部': '全部'
  };
  const paperType = typeMap[args[1]] || '全部';

  console.log(`🔍 搜索主题: ${query}`);
  console.log(`📋 文献类型: ${paperType}`);
  console.log();

  const queries = await generateSearchQueries(query, paperType);
  const output = formatOutput(queries);

  console.log(output);
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = { generateSearchQueries, saveNote };
