package core

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"runtime"
	"strings"
)

// Layout 上游源码布局版本
type Layout string

const (
	// LayoutV1 旧版布局: packages/opencode + script/build.ts + --single
	LayoutV1 Layout = "v1"
	// LayoutV2 新版布局: packages/cli + script/build.ts + --target=opencode-<platform> --outdir=<dist>
	LayoutV2 Layout = "v2"
)

// Builder 构建器
type Builder struct {
	opencodeDir string
	buildDir    string
	bunPath     string
	layout      Layout
}

// NewBuilder 创建构建器（自动检测布局）
// 可选传入 "v1" 或 "v2" 强制指定布局；空字符串则自动探测。
func NewBuilder(layout ...string) (*Builder, error) {
	opencodeDir, err := GetOpencodeDir()
	if err != nil {
		return nil, err
	}

	var l Layout
	if len(layout) > 0 && layout[0] != "" {
		l = ParseLayout(layout[0])
	} else {
		l = detectLayout(opencodeDir)
	}

	buildDir := filepath.Join(opencodeDir, "packages", "opencode")
	if l == LayoutV2 {
		buildDir = filepath.Join(opencodeDir, "packages", "cli")
	}

	bunPath := "bun" // 假设 bun 在 PATH 中

	// 简单的环境检查
	if _, err := Exec("bun", "--version"); err != nil {
		return nil, fmt.Errorf("未找到 Bun，请先安装: npm install -g bun")
	}

	return &Builder{
		opencodeDir: opencodeDir,
		buildDir:    buildDir,
		bunPath:     bunPath,
		layout:      l,
	}, nil
}

// ParseLayout 解析布局字符串
func ParseLayout(s string) Layout {
	switch strings.ToLower(strings.TrimSpace(s)) {
	case "v2", "2":
		return LayoutV2
	default:
		return LayoutV1
	}
}

// detectLayout 自动检测上游源码布局
// 优先判定为 V1（packages/opencode 存在），否则回退到 V2（packages/cli/script/build.ts 存在），再否则默认 V1。
func detectLayout(opencodeDir string) Layout {
	v1BuildDir := filepath.Join(opencodeDir, "packages", "opencode")
	if Exists(v1BuildDir) {
		return LayoutV1
	}

	v2BuildTS := filepath.Join(opencodeDir, "packages", "cli", "script", "build.ts")
	if Exists(v2BuildTS) {
		// 二次确认：V2 build.ts 已内建 --target= 能力
		if data, err := os.ReadFile(v2BuildTS); err == nil {
			if strings.Contains(string(data), "--target=") {
				return LayoutV2
			}
		}
	}

	return LayoutV1
}

// CheckEnvironment 检查构建环境
func (b *Builder) CheckEnvironment() error {
	if !Exists(b.buildDir) {
		return fmt.Errorf("构建目录不存在: %s", b.buildDir)
	}
	return nil
}

// PatchBunVersionCheck 修复 Bun 版本检查
// 支持两种上游模式：
//   - 旧版 (<=1.1.36): if (process.versions.bun !== expectedBunVersion) — 严格相等
//   - 新版 (>=1.1.37): semver.satisfies(process.versions.bun, expectedBunVersionRange) — 语义化范围
//
// 该补丁作用于 monorepo 级 packages/script/src/index.ts，V1/V2 共用同一文件。
func (b *Builder) PatchBunVersionCheck() (bool, error) {
	scriptPath := filepath.Join(b.opencodeDir, "packages", "script", "src", "index.ts")

	if !Exists(scriptPath) {
		return false, nil
	}

	contentBytes, err := os.ReadFile(scriptPath)
	if err != nil {
		return false, err
	}
	content := string(contentBytes)

	// 检查是否已经修复过（旧版补丁标记 或 新版补丁标记）
	if strings.Contains(content, "isCompatible") || strings.Contains(content, "// [opencode-i18n] version check bypassed") {
		return true, nil
	}

	patchApplied := false

	// === 模式 1: 新版 semver 检查 (>=1.1.37) ===
	semverCheck := "if (!semver.satisfies(process.versions.bun, expectedBunVersionRange))"
	if strings.Contains(content, semverCheck) {
		// 将 semver 检查替换为始终通过 + 仅打印警告
		lines := strings.Split(content, "\n")
		var newLines []string

		for i := 0; i < len(lines); i++ {
			line := lines[i]
			if strings.Contains(line, semverCheck) {
				// 替换为警告而非报错
				newLines = append(newLines, "// [opencode-i18n] version check bypassed: allow any bun version >= required")
				newLines = append(newLines, "if (!semver.satisfies(process.versions.bun, expectedBunVersionRange)) {")
				newLines = append(newLines, "  console.warn(`[opencode-i18n] Warning: expected bun@${expectedBunVersionRange}, using bun@${process.versions.bun}`)")
				newLines = append(newLines, "}")
				// 跳过原来的 throw 和 }
				i += 2
				patchApplied = true
			} else {
				newLines = append(newLines, line)
			}
		}

		if patchApplied {
			if err := os.WriteFile(scriptPath, []byte(strings.Join(newLines, "\n")), 0644); err != nil {
				return false, err
			}
			return true, nil
		}
	}

	// === 模式 2: 旧版严格相等检查 (<=1.1.36) ===
	strictCheck := "if (process.versions.bun !== expectedBunVersion)"
	if strings.Contains(content, strictCheck) {
		newCode := `// [opencode-i18n] version check bypassed: 放宽版本检查，允许使用相同或更高版本的 Bun
const [expectedMajor, expectedMinor, expectedPatch] = expectedBunVersion.split(".").map(Number)
const [actualMajor, actualMinor, actualPatch] = (process.versions.bun || "0.0.0").split(".").map(Number)

const isCompatible =
  actualMajor > expectedMajor ||
  (actualMajor === expectedMajor && actualMinor > expectedMinor) ||
  (actualMajor === expectedMajor && actualMinor === expectedMinor && actualPatch >= expectedPatch)

if (!isCompatible) {
  throw new Error(` + "`" + `This script requires bun@${expectedBunVersion}+, but you are using bun@${process.versions.bun}` + "`" + `)
}`

		lines := strings.Split(content, "\n")
		var newLines []string

		for i := 0; i < len(lines); i++ {
			line := lines[i]
			if strings.Contains(line, strictCheck) {
				newLines = append(newLines, newCode)
				// 跳过原来的 throw 和 }
				i += 2
				patchApplied = true
			} else {
				newLines = append(newLines, line)
			}
		}

		if patchApplied {
			if err := os.WriteFile(scriptPath, []byte(strings.Join(newLines, "\n")), 0644); err != nil {
				return false, err
			}
			return true, nil
		}
	}

	// 没有找到任何已知的版本检查模式，可能已被上游移除或使用新方式
	return false, nil
}

// InstallDependencies 安装依赖
// 上游是 monorepo 结构，需要从仓库根目录安装以解析 workspace 依赖
func (b *Builder) InstallDependencies(silent bool) error {
	if !silent {
		fmt.Println("正在安装依赖...")
	}

	// 先在 monorepo 根目录安装（如果存在根 package.json）
	// 上游仓库根目录 = buildDir 的祖父目录（V1: packages/opencode -> root；V2: packages/cli -> root）
	repoRoot := filepath.Dir(filepath.Dir(b.buildDir))
	rootPkgJSON := filepath.Join(repoRoot, "package.json")

	if Exists(rootPkgJSON) {
		rootNodeModules := filepath.Join(repoRoot, "node_modules")
		if !Exists(rootNodeModules) {
			if !silent {
				fmt.Printf("在 monorepo 根目录安装依赖: %s\n", repoRoot)
			}
			if err := os.Chdir(repoRoot); err != nil {
				return fmt.Errorf("切换到 monorepo 根目录失败: %w", err)
			}
			if err := ExecLive(b.bunPath, "install"); err != nil {
				return fmt.Errorf("monorepo 根目录 bun install 失败: %w", err)
			}
		} else if !silent {
			fmt.Println("monorepo 根目录依赖已存在")
		}
	}

	// 再在构建包目录安装（确保 workspace 本地依赖就绪）
	nodeModulesPath := filepath.Join(b.buildDir, "node_modules")
	if Exists(nodeModulesPath) {
		if !silent {
			fmt.Println("包级依赖已存在，跳过安装")
		}
		return nil
	}

	if err := os.Chdir(b.buildDir); err != nil {
		return err
	}

	return ExecLive(b.bunPath, "install")
}

// BuildArgs 返回构建命令参数（不执行）
// V1: run script/build.ts [--single]
// V2: run script/build.ts --target=opencode-<platform> --outdir=dist
func (b *Builder) BuildArgs(platform string) []string {
	args := []string{"run", "script/build.ts"}

	if platform != "" {
		if b.layout == LayoutV2 {
			args = append(args, "--target=opencode-"+platform, "--outdir=dist")
		} else {
			currentOs := runtime.GOOS
			currentArch := runtime.GOARCH

			targetParts := strings.Split(platform, "-")
			if len(targetParts) == 2 {
				targetOs := targetParts[0]
				if targetOs == "win32" {
					targetOs = "windows"
				}
				targetArch := targetParts[1]
				if currentArch == "amd64" {
					currentArch = "x64"
				}

				if targetOs == currentOs && targetArch == currentArch {
					args = append(args, "--single")
				}
			}
		}
	}

	return args
}

// Build 执行构建
func (b *Builder) Build(platform string, silent bool) error {
	if !silent {
		fmt.Println("开始编译构建...")
	}

	if err := b.CheckEnvironment(); err != nil {
		return err
	}

	if patched, err := b.PatchBunVersionCheck(); err != nil {
		fmt.Printf("警告: Bun 版本兼容性修复失败: %v\n", err)
	} else if patched && !silent {
		fmt.Println("  已应用 Bun 版本兼容性修复")
	}

	if err := b.InstallDependencies(silent); err != nil {
		return err
	}

	// Bun workspace hoist 修复：
	// 上游 monorepo 中 bun install 将关键包 hoist 到根 node_modules，
	// 但构建脚本通过 fs.realpathSync 在构建包本地 node_modules/ 下查找。
	// 需要确保关键包在本地 node_modules 可访问（通过 symlink 到根）。
	repoRoot := filepath.Dir(filepath.Dir(b.buildDir))
	b.ensureWorkspaceLinks(repoRoot, silent)

	args := b.BuildArgs(platform)

	if !silent {
		fmt.Printf("执行: %s %s\n", b.bunPath, strings.Join(args, " "))
	}

	if err := os.Chdir(b.buildDir); err != nil {
		return err
	}

	env := os.Environ()

	// 确保 OPENCODE_CHANNEL 默认设为 "latest"（避免 detached HEAD 导致 channel 为空，从而使用 opencode-.db）
	if _, exists := os.LookupEnv("OPENCODE_CHANNEL"); !exists {
		env = append(env, "OPENCODE_CHANNEL=latest")
	}

	// 用源码 package.json 的 version 固定嵌入版本号。
	// 上游 packages/script/src/index.ts 在 channel=latest 且未显式设 OPENCODE_VERSION 时，
	// 会 fetch npm @opencode/cli 的 latest 版本并 patch+1，导致从 v2.0.12 源码构建出 v2.0.13，
	// 与 git tag 不一致。显式设 OPENCODE_VERSION=<源码版本> 可让 --version 忠实反映所构建的源码。
	if _, exists := os.LookupEnv("OPENCODE_VERSION"); !exists {
		if v := b.sourceVersion(); v != "" {
			env = append(env, "OPENCODE_VERSION="+v)
		}
	}

	if err := ExecLiveEnv(b.bunPath, args, env); err != nil {
		return fmt.Errorf("bun 构建脚本执行失败: %w", err)
	}

	// 构建后验证：检查产物是否存在
	if platform != "" {
		distPath := b.GetDistPath(platform)
		if !Exists(distPath) {
			// 列出 dist 目录内容，帮助诊断
			distDir := filepath.Join(b.buildDir, "dist")
			if DirExists(distDir) {
				fmt.Printf("构建产物未找到: %s\n", distPath)
				fmt.Println("dist 目录内容:")
				entries, _ := os.ReadDir(distDir)
				for _, e := range entries {
					fmt.Printf("  %s (dir=%v)\n", e.Name(), e.IsDir())
					if e.IsDir() {
						subEntries, _ := os.ReadDir(filepath.Join(distDir, e.Name()))
						for _, se := range subEntries {
							fmt.Printf("    %s\n", se.Name())
						}
					}
				}
			} else {
				fmt.Printf("dist 目录不存在: %s\n", distDir)
				fmt.Println("构建可能完全失败，请检查上方 bun 输出日志")
			}
			return fmt.Errorf("构建产物验证失败: 期望路径 %s 不存在", distPath)
		}
		if !silent {
			fmt.Printf("✓ 构建产物已验证: %s\n", distPath)
		}
	}

	return nil
}

// ensureWorkspaceLinks 确保 workspace hoist 的包在本地 node_modules 可访问
// Bun workspace 将依赖 hoist 到根 node_modules，但构建脚本通过 fs.realpathSync
// 在构建包本地 node_modules/ 下查找。此方法创建必要的 symlink。
// V1 对应 packages/opencode/node_modules，V2 对应 packages/cli/node_modules。
func (b *Builder) ensureWorkspaceLinks(repoRoot string, silent bool) {
	rootNodeModules := filepath.Join(repoRoot, "node_modules")
	localNodeModules := filepath.Join(b.buildDir, "node_modules")

	if !DirExists(rootNodeModules) || !DirExists(localNodeModules) {
		return
	}

	// 需要确保可访问的关键包（构建脚本通过绝对路径引用）
	// V1/V2 目前共享 @opentui/* 包名；若 V2 改名，需在此更新（待构建验证）。
	criticalPackages := []string{"@opentui/core", "@opentui/solid"}

	for _, pkg := range criticalPackages {
		localPkg := filepath.Join(localNodeModules, pkg)
		rootPkg := filepath.Join(rootNodeModules, pkg)

		if Exists(localPkg) {
			continue // 已存在（可能是 symlink 或真实目录）
		}

		if !DirExists(rootPkg) {
			continue // 根目录也没有
		}

		// 确保父目录存在（@opentui 这样的 scoped 包需要）
		parentDir := filepath.Dir(localPkg)
		if err := EnsureDir(parentDir); err != nil {
			if !silent {
				fmt.Printf("警告: 创建目录 %s 失败: %v\n", parentDir, err)
			}
			continue
		}

		// 创建 symlink
		if err := os.Symlink(rootPkg, localPkg); err != nil {
			if !silent {
				fmt.Printf("警告: 创建 symlink %s -> %s 失败: %v\n", localPkg, rootPkg, err)
			}
		} else if !silent {
			fmt.Printf("  已创建 workspace link: %s -> %s\n", pkg, rootPkg)
		}
	}
}

// sourceVersion 读取构建包 package.json 的 version 字段
// V1: packages/opencode/package.json；V2: packages/cli/package.json（即 buildDir/package.json）。
// 读取失败返回空字符串（调用方据此跳过设置 OPENCODE_VERSION）。
func (b *Builder) sourceVersion() string {
	data, err := os.ReadFile(filepath.Join(b.buildDir, "package.json"))
	if err != nil {
		return ""
	}
	var pkg struct {
		Version string `json:"version"`
	}
	if err := json.Unmarshal(data, &pkg); err != nil {
		return ""
	}
	return pkg.Version
}

// GetDistPath 获取编译产物路径
// V1 产物布局: <buildDir>/dist/opencode-<platform>/bin/opencode[.exe]
// V2 产物布局: <buildDir>/dist/cli-<platform>/bin/opencode[.exe]
// 依据上游 packages/cli/script/build.ts: 输出目录名 = targetName(item).replace("opencode","cli")，
// 而 --target 仍为 opencode-<platform>，故 V2 的产物子目录是 cli-<platform> 而非 opencode-<platform>。
func (b *Builder) GetDistPath(platform string) string {
	ext := ""
	if strings.HasPrefix(platform, "windows") {
		ext = ".exe"
	}
	subdir := "opencode-" + platform
	if b.layout == LayoutV2 {
		subdir = "cli-" + platform
	}
	return filepath.Join(b.buildDir, "dist", subdir, "bin", "opencode"+ext)
}

// DeployToLocal 部署到本地 bin 目录 (统一目录: ~/.opencode-i18n/build)
func (b *Builder) DeployToLocal(platform string, silent bool) error {
	if !silent {
		fmt.Println("正在部署到本地环境...")
	}

	binDir, err := GetBinDir()
	if err != nil {
		return err
	}

	if err := EnsureDir(binDir); err != nil {
		return err
	}

	sourcePath := b.GetDistPath(platform)
	ext := ""
	if strings.HasPrefix(platform, "windows") {
		ext = ".exe"
	}
	destPath := filepath.Join(binDir, "opencode"+ext)

	if !Exists(sourcePath) {
		return fmt.Errorf("编译产物不存在: %s", sourcePath)
	}

	if err := CopyFile(sourcePath, destPath); err != nil {
		return err
	}

	if !silent {
		fmt.Printf("已部署到: %s\n", destPath)
	}
	return nil
}

// Layout 返回当前检测到的布局版本
func (b *Builder) Layout() Layout {
	return b.layout
}
