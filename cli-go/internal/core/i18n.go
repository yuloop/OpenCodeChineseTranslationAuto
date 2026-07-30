package core

import (
	"embed"
	"encoding/json"
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strings"
)

//go:embed assets/opencode-i18n
var embeddedAssets embed.FS

// TranslationConfig 汉化配置结构
type TranslationConfig struct {
	Category     string
	FileName     string
	ConfigPath   string
	File         string            `json:"file"`
	Replacements map[string]string `json:"replacements"`
}

// Replacement 单条替换规则（用于 verify 命令）
type Replacement struct {
	From string
	To   string
}

// GetReplacementsList 获取替换规则列表
func (c *TranslationConfig) GetReplacementsList() []Replacement {
	var list []Replacement
	for from, to := range c.Replacements {
		list = append(list, Replacement{From: from, To: to})
	}
	return list
}

// LoadI18nConfig 从单个 JSON 文件加载配置
func LoadI18nConfig(path string) (*TranslationConfig, error) {
	var config TranslationConfig
	if err := ReadJSON(path, &config); err != nil {
		return nil, err
	}
	config.ConfigPath = path
	return &config, nil
}

// I18n 汉化处理器
type I18n struct {
	i18nDir     string
	opencodeDir string
	useEmbedded bool
}

// NewI18n 创建 I18n 实例
func NewI18n() (*I18n, error) {
	i18nDir, err := GetI18nDir()
	useEmbedded := false

	// 如果获取目录失败或目录不存在，尝试使用内置资源
	if err != nil || !DirExists(i18nDir) {
		useEmbedded = true
		i18nDir = "assets/opencode-i18n" // embedded 中的相对路径
	}

	opencodeDir, err := GetOpencodeDir()
	if err != nil {
		// 如果连 OpenCode 源码目录都找不到，那就真的无法继续了
		return nil, err
	}

	if useEmbedded {
		fmt.Println("提示: 使用内置汉化配置")
	} else {
		fmt.Printf("提示: 使用外部汉化配置: %s\n", i18nDir)
	}

	return &I18n{
		i18nDir:     i18nDir,
		opencodeDir: opencodeDir,
		useEmbedded: useEmbedded,
	}, nil
}

// LoadConfig 读取所有汉化配置文件
func (i *I18n) LoadConfig() ([]TranslationConfig, error) {
	var configs []TranslationConfig
	var entries []fs.DirEntry
	var err error

	if i.useEmbedded {
		entries, err = fs.ReadDir(embeddedAssets, i.i18nDir)
	} else {
		entries, err = os.ReadDir(i.i18nDir)
	}

	if err != nil {
		return nil, err
	}

	for _, entry := range entries {
		if entry.IsDir() {
			// 处理子目录中的配置文件
			categoryName := entry.Name()

			var files []fs.DirEntry
			if i.useEmbedded {
				// Embedded FS 路径必须使用正斜杠
				embedPath := i.i18nDir + "/" + categoryName
				files, err = fs.ReadDir(embeddedAssets, embedPath)
			} else {
				categoryDir := filepath.Join(i.i18nDir, categoryName)
				files, err = os.ReadDir(categoryDir)
			}

			if err != nil {
				continue
			}

			for _, file := range files {
				if strings.HasSuffix(file.Name(), ".json") {
					config := i.loadSingleConfig(categoryName, file.Name())
					if config != nil {
						configs = append(configs, *config)
					}
				}
			}
		} else if strings.HasSuffix(entry.Name(), ".json") {
			// 处理根目录下的配置文件（如 app.json）
			// 跳过 config.json（元信息文件，不是汉化规则）
			if entry.Name() == "config.json" {
				continue
			}
			config := i.loadSingleConfig("root", entry.Name())
			if config != nil {
				configs = append(configs, *config)
			}
		}
	}

	return configs, nil
}

// loadSingleConfig 加载单个配置文件
func (i *I18n) loadSingleConfig(category, fileName string) *TranslationConfig {
	var config TranslationConfig
	var configPath string
	var readErr error

	if i.useEmbedded {
		if category == "root" {
			configPath = i.i18nDir + "/" + fileName
		} else {
			configPath = i.i18nDir + "/" + category + "/" + fileName
		}
		var data []byte
		data, readErr = fs.ReadFile(embeddedAssets, configPath)
		if readErr == nil {
			readErr = json.Unmarshal(data, &config)
		}
	} else {
		if category == "root" {
			configPath = filepath.Join(i.i18nDir, fileName)
		} else {
			configPath = filepath.Join(i.i18nDir, category, fileName)
		}
		readErr = ReadJSON(configPath, &config)
	}

	if readErr != nil {
		fmt.Printf("警告: 解析配置文件失败 %s: %v\n", configPath, readErr)
		return nil
	}

	config.Category = category
	config.FileName = fileName
	config.ConfigPath = configPath
	return &config
}

// ApplyResult 应用结果
type ApplyResult struct {
	File         string
	Success      bool
	Replacements struct {
		Total   int
		Success int
		Failed  int
	}
	Skipped    bool
	SkipReason string
}

type pendingReplacement struct {
	find        string
	replace     string
	simpleWord  bool
	configIndex int
}

// GetTargetFilePath 获取汉化配置对应的目标文件完整路径
// 统一 verify 和 apply 的路径处理逻辑
// opencode 1.18.2+ 将 TUI 代码从 packages/opencode/src/cli/cmd/tui/ 移到 packages/tui/src/
func (i *I18n) GetTargetFilePath(config TranslationConfig) string {
	if config.File == "" {
		return ""
	}

	relativePath := config.File
	if !strings.HasPrefix(relativePath, "packages/") {
		if strings.HasPrefix(relativePath, "src/cli/cmd/tui/") {
			rest := strings.TrimPrefix(relativePath, "src/cli/cmd/tui/")
			relativePath = filepath.Join("packages", "tui", "src", rest)
		} else {
			relativePath = filepath.Join("packages", "opencode", relativePath)
		}
	}

	return filepath.Join(i.opencodeDir, relativePath)
}

// ApplyConfig 应用单个配置文件的替换规则
func (i *I18n) ApplyConfig(config TranslationConfig, dryRun bool) ApplyResult {
	return i.ApplyConfigs([]TranslationConfig{config}, dryRun)[0]
}

// ApplyConfigs 原子地应用一组配置。
// 指向同一源码文件的配置会基于同一份原文匹配，避免相互覆盖导致误报漏匹配。
func (i *I18n) ApplyConfigs(configs []TranslationConfig, dryRun bool) []ApplyResult {
	results := make([]ApplyResult, len(configs))
	configsByTarget := make(map[string][]int)

	for index, config := range configs {
		results[index].File = config.File
		results[index].Replacements.Total = len(config.Replacements)

		if config.File == "" || len(config.Replacements) == 0 {
			results[index].Skipped = true
			results[index].SkipReason = "缺少 file 或 replacements 字段"
			continue
		}

		targetPath := i.GetTargetFilePath(config)
		if !Exists(targetPath) {
			results[index].Skipped = true
			results[index].SkipReason = "目标文件不存在"
			results[index].Replacements.Failed = results[index].Replacements.Total
			continue
		}

		configsByTarget[targetPath] = append(configsByTarget[targetPath], index)
	}

	targetPaths := make([]string, 0, len(configsByTarget))
	for targetPath := range configsByTarget {
		targetPaths = append(targetPaths, targetPath)
	}
	sort.Strings(targetPaths)

	for _, targetPath := range targetPaths {
		configIndexes := configsByTarget[targetPath]
		contentBytes, err := os.ReadFile(targetPath)
		if err != nil {
			for _, configIndex := range configIndexes {
				results[configIndex].Skipped = true
				results[configIndex].SkipReason = fmt.Sprintf("读取文件失败: %v", err)
				results[configIndex].Replacements.Failed = results[configIndex].Replacements.Total
			}
			continue
		}

		originalContent := strings.ReplaceAll(string(contentBytes), "\r\n", "\n")
		var replacements []pendingReplacement

		for _, configIndex := range configIndexes {
			config := configs[configIndex]
			for find, replace := range config.Replacements {
				normalizedFind := strings.ReplaceAll(find, "\r\n", "\n")
				isSimpleWord, _ := regexp.MatchString("^[a-zA-Z0-9]+$", normalizedFind)
				replacement := pendingReplacement{
					find:        normalizedFind,
					replace:     replace,
					simpleWord:  isSimpleWord,
					configIndex: configIndex,
				}

				if replacementMatches(originalContent, replacement) {
					results[configIndex].Replacements.Success++
					replacements = append(replacements, replacement)
				} else {
					results[configIndex].Replacements.Failed++
				}
			}
			results[configIndex].Success = results[configIndex].Replacements.Success > 0
		}

		if dryRun {
			continue
		}

		content := applyReplacements(originalContent, replacements)
		if content == originalContent {
			continue
		}

		if err := os.WriteFile(targetPath, []byte(content), 0644); err != nil {
			fmt.Printf("错误: 写入文件失败 %s: %v\n", targetPath, err)
			for _, configIndex := range configIndexes {
				results[configIndex].Success = false
			}
		}
	}

	return results
}

func replacementMatches(content string, replacement pendingReplacement) bool {
	if replacement.find == "" {
		return false
	}
	if replacement.simpleWord {
		pattern := regexp.MustCompile(`\b` + regexp.QuoteMeta(replacement.find) + `\b`)
		return pattern.MatchString(content)
	}
	return strings.Contains(content, replacement.find)
}

func applyReplacements(content string, replacements []pendingReplacement) string {
	sort.SliceStable(replacements, func(left, right int) bool {
		if len(replacements[left].find) != len(replacements[right].find) {
			return len(replacements[left].find) > len(replacements[right].find)
		}
		if replacements[left].find != replacements[right].find {
			return replacements[left].find < replacements[right].find
		}
		if replacements[left].configIndex != replacements[right].configIndex {
			return replacements[left].configIndex < replacements[right].configIndex
		}
		return replacements[left].replace < replacements[right].replace
	})

	type stagedReplacement struct {
		placeholder string
		replace     string
	}

	var staged []stagedReplacement
	for index, replacement := range replacements {
		placeholder := fmt.Sprintf("\x00opencode-i18n-%d\x00", index)
		updated := content
		if replacement.simpleWord {
			pattern := regexp.MustCompile(`\b` + regexp.QuoteMeta(replacement.find) + `\b`)
			updated = pattern.ReplaceAllStringFunc(content, func(string) string {
				return placeholder
			})
		} else {
			updated = strings.ReplaceAll(content, replacement.find, placeholder)
		}

		if updated == content {
			continue
		}
		content = updated
		staged = append(staged, stagedReplacement{
			placeholder: placeholder,
			replace:     replacement.replace,
		})
	}

	for _, replacement := range staged {
		content = strings.ReplaceAll(content, replacement.placeholder, replacement.replace)
	}
	return content
}
