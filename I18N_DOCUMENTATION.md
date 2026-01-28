# 多语言支持文档 / Multi-Language Support Documentation

## 概述 / Overview

应用现已支持4种语言的完整国际化：
- 🇬🇧 English (英语)
- 🇨🇳 简体中文 (Simplified Chinese)
- 🇹🇼 繁體中文 (Traditional Chinese)
- 🇯🇵 日本語 (Japanese)

The application now supports full internationalization in 4 languages:
- 🇬🇧 English
- 🇨🇳 Simplified Chinese (简体中文)
- 🇹🇼 Traditional Chinese (繁體中文)
- 🇯🇵 Japanese (日本語)

## 使用方法 / Usage

### 通过URL参数切换语言 / Switch Language via URL Parameter

在任何页面URL后添加 `?lang=` 参数：
Add `?lang=` parameter to any page URL:

```
https://notiontoword.space/?lang=en        # English
https://notiontoword.space/?lang=zh_CN     # 简体中文
https://notiontoword.space/?lang=zh_TW     # 繁體中文
https://notiontoword.space/?lang=ja        # 日本語
```

### 使用语言切换器 / Use Language Switcher

点击导航栏右侧的语言按钮（🌐）选择语言。
Click the language button (🌐) on the right side of the navigation bar to select a language.

### 自动语言检测 / Automatic Language Detection

如果未指定语言，应用会按以下顺序检测：
If no language is specified, the app detects in this order:

1. URL参数 `?lang=` / URL parameter `?lang=`
2. Session中保存的语言 / Language saved in session
3. 浏览器Accept-Language头 / Browser Accept-Language header
4. 默认英语 / Default to English

## 技术实现 / Technical Implementation

### 使用的技术 / Technologies Used

- **Flask-Babel 4.0.0**: Flask的国际化扩展 / Flask i18n extension
- **gettext**: GNU国际化标准 / GNU internationalization standard
- **.po/.mo文件**: 翻译文件格式 / Translation file format

### 文件结构 / File Structure

```
notion_tools/
├── app.py                          # Flask应用配置 / Flask app configuration
├── babel.cfg                       # Babel配置文件 / Babel config file
├── translations/                   # 翻译目录 / Translations directory
│   ├── zh_CN/                     # 简体中文 / Simplified Chinese
│   │   └── LC_MESSAGES/
│   │       ├── messages.po        # 翻译源文件 / Translation source
│   │       └── messages.mo        # 编译后的翻译 / Compiled translation
│   ├── zh_TW/                     # 繁體中文 / Traditional Chinese
│   │   └── LC_MESSAGES/
│   │       ├── messages.po
│   │       └── messages.mo
│   └── ja/                        # 日本語 / Japanese
│       └── LC_MESSAGES/
│           ├── messages.po
│           └── messages.mo
└── templates/
    └── index.html                 # 使用gettext的模板 / Template using gettext
```

### Flask-Babel配置 / Flask-Babel Configuration

在 `app.py` 中：
In `app.py`:

```python
from flask_babel import Babel, gettext, get_locale

# Babel配置 / Babel configuration
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_SUPPORTED_LOCALES'] = ['en', 'zh_CN', 'zh_TW', 'ja']
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'

babel = Babel(app)

def get_locale():
    """确定用户的最佳语言 / Determine the best locale for the user"""
    # 1. 检查URL参数 / Check URL parameter
    lang = request.args.get('lang')
    if lang in app.config['BABEL_SUPPORTED_LOCALES']:
        session['language'] = lang
        return lang

    # 2. 检查session / Check session
    if 'language' in session:
        return session['language']

    # 3. 检查浏览器Accept-Language / Check browser Accept-Language
    return request.accept_languages.best_match(
        app.config['BABEL_SUPPORTED_LOCALES']
    ) or 'en'

babel.init_app(app, locale_selector=get_locale)
```

### 模板中使用翻译 / Using Translations in Templates

```html
<!-- 简单文本翻译 / Simple text translation -->
<h1>{{ gettext('Document Converter') }}</h1>

<!-- 带变量的翻译 / Translation with variables -->
<p>{{ gettext('Welcome, %(name)s!', name=user.name) }}</p>

<!-- 复数形式 / Plural forms -->
<p>{{ ngettext('%(num)d file', '%(num)d files', count) }}</p>
```

## 添加新语言 / Adding New Languages

### 1. 创建新的语言目录 / Create New Language Directory

```bash
mkdir -p translations/[locale_code]/LC_MESSAGES
```

例如添加韩语 / For example, to add Korean:
```bash
mkdir -p translations/ko/LC_MESSAGES
```

### 2. 创建翻译文件 / Create Translation File

复制现有的 `.po` 文件并翻译：
Copy an existing `.po` file and translate:

```bash
cp translations/zh_CN/LC_MESSAGES/messages.po translations/ko/LC_MESSAGES/messages.po
```

编辑 `messages.po` 文件，翻译所有 `msgstr` 字段。
Edit the `messages.po` file and translate all `msgstr` fields.

### 3. 编译翻译文件 / Compile Translation File

```bash
pybabel compile -d translations
```

### 4. 更新应用配置 / Update App Configuration

在 `app.py` 中添加新语言：
Add the new language in `app.py`:

```python
app.config['BABEL_SUPPORTED_LOCALES'] = ['en', 'zh_CN', 'zh_TW', 'ja', 'ko']
```

在 `inject_locale()` 函数中添加：
Add in the `inject_locale()` function:

```python
'available_locales': {
    'en': 'English',
    'zh_CN': '简体中文',
    'zh_TW': '繁體中文',
    'ja': '日本語',
    'ko': '한국어'  # 新增 / New
}
```

## 更新翻译 / Updating Translations

### 1. 提取新的可翻译字符串 / Extract New Translatable Strings

```bash
pybabel extract -F babel.cfg -o messages.pot .
```

### 2. 更新现有翻译文件 / Update Existing Translation Files

```bash
pybabel update -i messages.pot -d translations
```

### 3. 编辑翻译文件 / Edit Translation Files

打开 `translations/[locale]/LC_MESSAGES/messages.po` 并翻译新添加的字符串。
Open `translations/[locale]/LC_MESSAGES/messages.po` and translate newly added strings.

### 4. 编译翻译 / Compile Translations

```bash
pybabel compile -d translations
```

## 翻译文件格式 / Translation File Format

`.po` 文件示例 / Example `.po` file:

```po
# 注释 / Comment
msgid "Document Converter"
msgstr "文档转换器"

# 带上下文的翻译 / Translation with context
msgctxt "button"
msgid "Convert"
msgstr "转换"

# 复数形式 / Plural forms
msgid "%(num)d file"
msgid_plural "%(num)d files"
msgstr[0] "%(num)d个文件"
```

## 语言代码 / Language Codes

| 语言 / Language | 代码 / Code | 显示名称 / Display Name |
|----------------|-------------|------------------------|
| 英语 / English | `en` | English |
| 简体中文 / Simplified Chinese | `zh_CN` | 简体中文 |
| 繁體中文 / Traditional Chinese | `zh_TW` | 繁體中文 |
| 日本語 / Japanese | `ja` | 日本語 |

## SEO优化 / SEO Optimization

### 语言特定的Meta标签 / Language-Specific Meta Tags

每种语言应该有自己的meta标签（未来改进）：
Each language should have its own meta tags (future improvement):

```html
{% if current_locale == 'zh_CN' %}
<meta name="description" content="免费在线文档转换工具...">
{% elif current_locale == 'ja' %}
<meta name="description" content="無料のオンライン文書変換ツール...">
{% else %}
<meta name="description" content="Free online document converter...">
{% endif %}
```

### hreflang标签 / hreflang Tags

为SEO添加hreflang标签（未来改进）：
Add hreflang tags for SEO (future improvement):

```html
<link rel="alternate" hreflang="en" href="https://notiontoword.space/?lang=en">
<link rel="alternate" hreflang="zh-CN" href="https://notiontoword.space/?lang=zh_CN">
<link rel="alternate" hreflang="zh-TW" href="https://notiontoword.space/?lang=zh_TW">
<link rel="alternate" hreflang="ja" href="https://notiontoword.space/?lang=ja">
```

## 测试 / Testing

### 本地测试 / Local Testing

```bash
# 启动应用 / Start the app
python app.py

# 测试不同语言 / Test different languages
http://localhost:5000/?lang=en
http://localhost:5000/?lang=zh_CN
http://localhost:5000/?lang=zh_TW
http://localhost:5000/?lang=ja
```

### 验证翻译 / Verify Translations

1. 检查所有页面元素是否正确翻译 / Check all page elements are translated correctly
2. 测试语言切换器 / Test language switcher
3. 验证URL参数是否工作 / Verify URL parameters work
4. 检查session是否保持语言选择 / Check session maintains language choice

## 常见问题 / FAQ

### Q: 为什么我的翻译没有显示？
**A**: 确保已编译翻译文件：`pybabel compile -d translations`

### Q: Why aren't my translations showing?
**A**: Make sure you've compiled the translation files: `pybabel compile -d translations`

### Q: 如何添加新的可翻译字符串？
**A**: 在模板中使用 `{{ gettext('Your text') }}`，然后运行 `pybabel extract` 和 `pybabel update`

### Q: How do I add new translatable strings?
**A**: Use `{{ gettext('Your text') }}` in templates, then run `pybabel extract` and `pybabel update`

### Q: 语言切换后为什么有些文本还是英文？
**A**: 可能是该文本还没有添加到翻译文件中，或者翻译文件没有编译

### Q: Why is some text still in English after switching languages?
**A**: The text might not be added to translation files yet, or translation files aren't compiled

## 贡献翻译 / Contributing Translations

欢迎贡献新的翻译或改进现有翻译！
Contributions for new translations or improvements to existing ones are welcome!

1. Fork仓库 / Fork the repository
2. 编辑 `.po` 文件 / Edit `.po` files
3. 编译翻译 / Compile translations
4. 测试更改 / Test changes
5. 提交Pull Request / Submit Pull Request

## 相关文件 / Related Files

- `app.py` - Flask-Babel配置 / Flask-Babel configuration
- `babel.cfg` - Babel配置 / Babel configuration
- `translations/` - 所有翻译文件 / All translation files
- `templates/index.html` - 使用gettext的主模板 / Main template using gettext
- `requirements.txt` - 包含Flask-Babel依赖 / Includes Flask-Babel dependency

## 更新日志 / Changelog

### 2026-01-28
- ✅ 添加Flask-Babel支持 / Added Flask-Babel support
- ✅ 创建4种语言的翻译文件 / Created translation files for 4 languages
- ✅ 实现语言切换器UI / Implemented language switcher UI
- ✅ 添加URL语言控制 / Added URL language control
- ✅ 更新所有模板文本使用gettext / Updated all template text to use gettext
- ✅ 添加session语言持久化 / Added session language persistence
