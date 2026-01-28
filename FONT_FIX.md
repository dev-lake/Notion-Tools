# 修复：Word中文字符显示为豆腐块问题

## 问题描述

转换后的Word文档在WPS中打开正常，但在Microsoft Word中打开时，部分中文、日文、韩文等字符显示为方块（豆腐块）。

## 根本原因

这是字体设置问题。python-docx库在创建文档时，如果不明确设置东亚字体（East Asian fonts），Microsoft Word会使用默认字体，而该字体可能不支持CJK（中日韩）字符，导致显示为方块。

WPS对字体的处理更宽容，会自动选择合适的字体，所以在WPS中显示正常。

## 解决方案

### 1. 添加字体设置函数

创建了 `_set_font()` 函数，为所有文本明确设置字体：

```python
def _set_font(run, is_code=False):
    """设置字体以确保Microsoft Word兼容性"""
    if is_code:
        # 代码使用等宽字体
        run.font.name = 'Consolas'
        run.font.size = Pt(9)
        run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
    else:
        # 普通文本
        run.font.name = 'Calibri'
        # 东亚字体（中日韩）
        run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
        # ASCII字符字体
        run._element.rPr.rFonts.set(qn('w:ascii'), 'Calibri')
        # 复杂字符字体
        run._element.rPr.rFonts.set(qn('w:hAnsi'), 'Calibri')
```

### 2. 字体选择说明

**普通文本：**
- ASCII字符：Calibri（Word默认字体，兼容性好）
- 东亚字符：Microsoft YaHei（微软雅黑，Windows系统自带）

**代码文本：**
- ASCII字符：Consolas（等宽字体，适合代码）
- 东亚字符：Microsoft YaHei（支持中文的等宽显示）

### 3. 应用范围

字体设置已应用到所有文本元素：
- ✅ 标题（H1-H6）
- ✅ 段落文本
- ✅ 粗体和斜体
- ✅ 列表项
- ✅ 表格单元格
- ✅ 代码块
- ✅ 行内代码
- ✅ 链接文本

## 技术细节

### Word字体属性

Word文档使用多个字体属性来处理不同类型的字符：

1. **w:ascii** - ASCII字符（0-127）
2. **w:eastAsia** - 东亚字符（中文、日文、韩文）
3. **w:hAnsi** - 高位ANSI字符（128-255）
4. **w:cs** - 复杂脚本字符（阿拉伯文、希伯来文等）

我们的修复设置了前三个属性，确保所有常见字符都能正确显示。

### 为��么选择这些字体？

**Microsoft YaHei（微软雅黑）：**
- ✅ Windows Vista及以上系统自带
- ✅ 支持简体中文、繁体中文
- ✅ 支持日文假名和常用汉字
- ✅ 支持韩文
- ✅ 显示效果清晰美观

**Calibri：**
- ✅ Word 2007+默认字体
- ✅ 所有Windows系统自带
- ✅ 专业、现代的外观
- ✅ 屏幕显示优化

**Consolas：**
- ✅ 等宽字体，适合代码
- ✅ Windows Vista及以上自带
- ✅ 字符区分度高（0/O, 1/l/I等）

## 测试

创建了测试文件 `test_data/test_chinese.md`，包含：
- 中文、日文、韩文字符
- 粗体、斜体、代码
- 表格、列表、引用
- 特殊符号

转换后的文档在Microsoft Word中应该能正确显示所有字符。

## 兼容性

### 支持的系统

**Windows：**
- ✅ Windows Vista及以上（包含所需字体）
- ⚠️ Windows XP需要安装微软雅黑字体

**macOS：**
- ✅ 所有版本（系统会自动替换为等效字体）
- 中文会使用"苹方"或"华文黑体"

**Linux：**
- ⚠️ 需要安装Microsoft字体包
- 或者修改代码使用系统字体（如Noto Sans CJK）

### 支持的Word��本

- ✅ Microsoft Word 2007及以上
- ✅ Microsoft Word for Mac
- ✅ WPS Office
- ✅ LibreOffice Writer
- ✅ Google Docs（导入后）

## 替代字体方案

如果需要在Linux或其他系统上使用，可以修改 `_set_font()` 函数：

```python
# Linux系统推荐使用Noto字体
run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Noto Sans CJK SC')

# macOS系统推荐使用苹方
run._element.rPr.rFonts.set(qn('w:eastAsia'), 'PingFang SC')

# 通用方案（使用宋体）
run._element.rPr.rFonts.set(qn('w:eastAsia'), 'SimSun')
```

## 验证修复

### 测试步骤

1. 上传包含中文的Notion导出
2. 转换为Word文档
3. 在Microsoft Word中打开
4. 检查所有中文字符是否正常显示

### 预期结果

- ✅ 所有中文字符正常显示
- ✅ 日文、韩文字符正常显示
- ✅ 英文字符正常显示
- ✅ 代���块中的中文注释正常显示
- ✅ 表格中的中文正常显示
- ✅ 标题中的中文正常显示

## 相关文件

- `converter.py` - 主要修改文件
- `test_data/test_chinese.md` - 测试用Markdown文件
- `test_data/test_chinese_output.docx` - 测试输出文档

## 参考资料

- [python-docx Font documentation](https://python-docx.readthedocs.io/en/latest/api/text.html#font-objects)
- [Office Open XML Font specification](http://officeopenxml.com/WPtextFormatting.php)
- [Microsoft Word Font handling](https://docs.microsoft.com/en-us/typography/font-list/)
