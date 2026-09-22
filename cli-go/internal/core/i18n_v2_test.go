package core

import (
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
	total := 0
	for _, config := range configs {
		if config.File == "" {
			t.Errorf("V2 规则 %s 缺少 file 字段", config.FileName)
		}
		if config.FileName == "config.json" {
			t.Errorf("config.json 是元信息文件，不应作为规则加载")
		}
		total += len(config.Replacements)
	}
	// 分母不变：V2 资产保留全部 497 条（迁移不动的保留旧锚点）
	if total != 497 {
		t.Errorf("V2 资产条目数应为 497(分母不变): got %d", total)
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
