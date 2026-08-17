# OpenCode 汉化版【实时预览版】一键安装入口（Windows）
# 复用 install.ps1：注入 $script:Preview = $true，使其按预览版方式安装
# （独立目录 %LOCALAPPDATA%\opencode-i18n-preview，与正式版互不影响；重跑同一命令即更新）
$script:Preview = $true
& ([scriptblock]::Create((irm 'https://raw.githubusercontent.com/yuloop/OpenCodeChineseTranslationAuto/main/install.ps1' -UseBasicParsing)))