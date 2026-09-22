package core

import (
	"encoding/json"
	"io/fs"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// makeProjectRoot 构造一个最小项目根（含 cli-go 目录，满足 isProjectRoot）
func makeProjectRoot(t *testing.T) string {
	t.Helper()
	dir := t.TempDir()
	if err := os.MkdirAll(filepath.Join(dir, "cli-go"), 0755); err != nil {
		t.Fatalf("创建 cli-go 目录失败: %v", err)
	}
	return dir
}

// ========== GetI18nDirForLayout 测试 ==========

func TestGetI18nDirForLayoutV2PrefersExternalOverAssets(t *testing.T) {
	project := makeProjectRoot(t)
	t.Setenv("OPENCODE_PROJECT_DIR", project)

	external := filepath.Join(project, "opencode-i18n-v2")
	assets := filepath.Join(project, "cli-go", "internal", "core", "assets", "opencode-i18n-v2")
	for _, dir := range []string{external, assets} {
		if err := os.MkdirAll(dir, 0755); err != nil {
			t.Fatalf("创建目录失败 %s: %v", dir, err)
		}
	}

	got, err := GetI18nDirForLayout(LayoutV2)
	if err != nil {
		t.Fatalf("GetI18nDirForLayout 返回错误: %v", err)
	}
	if got != external {
		t.Errorf("V2 布局应优先外部 opencode-i18n-v2: got %q, want %q", got, external)
	}
}

func TestGetI18nDirForLayoutV2FallsBackToAssets(t *testing.T) {
	project := makeProjectRoot(t)
	t.Setenv("OPENCODE_PROJECT_DIR", project)

	assets := filepath.Join(project, "cli-go", "internal", "core", "assets", "opencode-i18n-v2")
	if err := os.MkdirAll(assets, 0755); err != nil {
		t.Fatalf("创建目录失败 %s: %v", assets, err)
	}

	got, err := GetI18nDirForLayout(LayoutV2)
	if err != nil {
		t.Fatalf("GetI18nDirForLayout 返回错误: %v", err)
	}
	if got != assets {
		t.Errorf("V2 布局无外部目录时应回落 assets: got %q, want %q", got, assets)
	}
}

func TestGetI18nDirForLayoutV2EmptyWhenMissing(t *testing.T) {
	project := makeProjectRoot(t)
	t.Setenv("OPENCODE_PROJECT_DIR", project)

	got, err := GetI18nDirForLayout(LayoutV2)
	if err != nil {
		t.Fatalf("GetI18nDirForLayout 返回错误: %v", err)
	}
	if got != "" {
		t.Errorf("V2 资产缺失时应返回空(走内嵌): got %q", got)
	}
}

func TestGetI18nDirForLayoutV1NeverPicksV2Assets(t *testing.T) {
	// V1 布局必须沿用历史解析（不得染指 V2 资产目录）
	got, err := GetI18nDirForLayout(LayoutV1)
	if err != nil {
		t.Fatalf("GetI18nDirForLayout 返回错误: %v", err)
	}
	if got == "" {
		t.Skip("当前环境无外部 V1 资产目录（将走内嵌），跳过路径断言")
	}
	if strings.HasSuffix(got, "opencode-i18n-v2") {
		t.Errorf("V1 布局不应返回 V2 资产目录: %q", got)
	}
	if !strings.HasSuffix(got, "opencode-i18n") {
		t.Errorf("V1 布局应返回 V1 资产目录: %q", got)
	}
}

// ========== 资产加载测试 ==========

func loadEmbedded(t *testing.T, dir string, embedded fs.FS) []TranslationConfig {
	t.Helper()
	i18n := &I18n{i18nDir: dir, useEmbedded: true, embedded: embedded}
	configs, err := i18n.LoadConfig()
	if err != nil {
		t.Fatalf("LoadConfig(%s) 失败: %v", dir, err)
	}
	return configs
}

func TestEmbeddedV1AssetsUnchanged(t *testing.T) {
	configs := loadEmbedded(t, "assets/opencode-i18n", embeddedAssets)
	if len(configs) != 54 {
		t.Errorf("V1 规则文件数应保持 54: got %d", len(configs))
	}
	total := 0
	for _, config := range configs {
		if config.File == "" {
			t.Errorf("V1 规则 %s 缺少 file 字段", config.FileName)
		}
		total += len(config.Replacements)
	}
	if total != 497 {
		t.Errorf("V1 翻译条目数应保持 497: got %d", total)
	}
}

func TestEmbeddedV2AssetsLoadAndSkipMeta(t *testing.T) {
	configs := loadEmbedded(t, "assets/opencode-i18n-v2", embeddedAssetsV2)
	if len(configs) == 0 {
		t.Fatal("V2 资产加载结果为空")
	}
	for _, config := range configs {
		if config.File == "" {
			t.Errorf("V2 规则 %s 缺少 file 字段", config.FileName)
		}
		if config.FileName == "config.json" {
			t.Errorf("config.json 是元信息文件，不应作为规则加载")
		}
	}
}

// TestEmbeddedV2AssetsCoverEveryV1Entry 保证「条目不丢」：V1 词表的每一条
// (规则, 原文) 都必须在 V2 资产的 manifest 里有对应条目。
// 注意：同一 UI 串在 V2 多处等价位置出现时会逐处锚定，因此 V2 的规则文件键数
// 会多于 V1 条目数（门禁分母随之变大）；这里断言的是覆盖关系，不是键数相等。
func TestEmbeddedV2AssetsCoverEveryV1Entry(t *testing.T) {
	type entry struct{ rule, key string }

	// V1 的 FileName 只是 basename，规则相对路径要拼上 Category（root 级除外）
	rulePath := func(category, fileName string) string {
		if category == "root" {
			return fileName
		}
		return category + "/" + fileName
	}

	want := map[entry]struct{}{}
	for _, config := range loadEmbedded(t, "assets/opencode-i18n", embeddedAssets) {
		for key := range config.Replacements {
			want[entry{rulePath(config.Category, config.FileName), key}] = struct{}{}
		}
	}

	raw, err := fs.ReadFile(embeddedAssetsV2, "assets/opencode-i18n-v2/config.json")
	if err != nil {
		t.Fatalf("读取 V2 config.json 失败: %v", err)
	}
	var meta struct {
		Manifest struct {
			Entries []struct {
				Rule string `json:"rule"`
				Key  string `json:"key"`
			} `json:"entries"`
		} `json:"manifest"`
	}
	if err := json.Unmarshal(raw, &meta); err != nil {
		t.Fatalf("解析 V2 config.json 失败: %v", err)
	}

	got := make(map[entry]struct{}, len(meta.Manifest.Entries))
	for _, e := range meta.Manifest.Entries {
		got[entry{e.Rule, e.Key}] = struct{}{}
	}
	for e := range want {
		if _, ok := got[e]; !ok {
			t.Errorf("V1 条目在 V2 资产中丢失: %s / %q", e.rule, e.key)
		}
	}
	if len(got) < len(want) {
		t.Errorf("V2 资产条目数不应少于 V1: got %d, want >= %d", len(got), len(want))
	}
}

func TestNewI18nSelectsAssetsByLayout(t *testing.T) {
	// V2 布局源码（packages/cli/script/build.ts 含 --target=）
	v2Source := t.TempDir()
	buildTS := filepath.Join(v2Source, "packages", "cli", "script", "build.ts")
	if err := os.MkdirAll(filepath.Dir(buildTS), 0755); err != nil {
		t.Fatalf("创建目录失败: %v", err)
	}
	if err := os.WriteFile(buildTS, []byte("const requestedTarget = process.argv.find((arg) => arg.startsWith(\"--target=\"))"), 0644); err != nil {
		t.Fatalf("写入 build.ts 失败: %v", err)
	}
	t.Setenv("OPENCODE_SOURCE_DIR", v2Source)

	i18n, err := NewI18n()
	if err != nil {
		t.Fatalf("NewI18n(V2) 失败: %v", err)
	}
	if !strings.HasSuffix(i18n.i18nDir, "opencode-i18n-v2") {
		t.Errorf("V2 布局应选 V2 资产: got %q", i18n.i18nDir)
	}

	// V1 布局源码（packages/opencode 存在）
	v1Source := t.TempDir()
	if err := os.MkdirAll(filepath.Join(v1Source, "packages", "opencode"), 0755); err != nil {
		t.Fatalf("创建目录失败: %v", err)
	}
	t.Setenv("OPENCODE_SOURCE_DIR", v1Source)

	i18n, err = NewI18n()
	if err != nil {
		t.Fatalf("NewI18n(V1) 失败: %v", err)
	}
	if strings.HasSuffix(i18n.i18nDir, "opencode-i18n-v2") {
		t.Errorf("V1 布局不应选 V2 资产: got %q", i18n.i18nDir)
	}
	if i18n.useEmbedded && !strings.HasSuffix(i18n.i18nDir, "opencode-i18n") {
		t.Errorf("V1 布局内嵌资产路径应为 assets/opencode-i18n: got %q", i18n.i18nDir)
	}
}
