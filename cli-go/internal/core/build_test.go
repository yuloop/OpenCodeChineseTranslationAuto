package core

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestDetectLayoutV1(t *testing.T) {
	tmpDir := t.TempDir()
	if err := os.MkdirAll(filepath.Join(tmpDir, "packages", "opencode"), 0755); err != nil {
		t.Fatalf("mkdir: %v", err)
	}
	if err := os.WriteFile(filepath.Join(tmpDir, "packages", "opencode", "package.json"), []byte("{}"), 0644); err != nil {
		t.Fatalf("write: %v", err)
	}

	got := detectLayout(tmpDir)
	if got != LayoutV1 {
		t.Errorf("detectLayout V1 = %q, want %q", got, LayoutV1)
	}
}

func TestDetectLayoutV2(t *testing.T) {
	tmpDir := t.TempDir()
	if err := os.MkdirAll(filepath.Join(tmpDir, "packages", "cli", "script"), 0755); err != nil {
		t.Fatalf("mkdir: %v", err)
	}
	buildTS := `const singleFlag = process.argv.includes("--single")
const requestedTarget = process.argv.find((arg) => arg.startsWith("--target="))?.slice("--target=".length)`
	if err := os.WriteFile(filepath.Join(tmpDir, "packages", "cli", "script", "build.ts"), []byte(buildTS), 0644); err != nil {
		t.Fatalf("write: %v", err)
	}

	got := detectLayout(tmpDir)
	if got != LayoutV2 {
		t.Errorf("detectLayout V2 = %q, want %q", got, LayoutV2)
	}
}

func TestDetectLayoutFallbackToV1(t *testing.T) {
	tmpDir := t.TempDir()
	got := detectLayout(tmpDir)
	if got != LayoutV1 {
		t.Errorf("detectLayout fallback = %q, want %q", got, LayoutV1)
	}
}

func TestParseLayout(t *testing.T) {
	cases := []struct {
		in   string
		want Layout
	}{
		{"v1", LayoutV1},
		{"V1", LayoutV1},
		{"v2", LayoutV2},
		{"V2", LayoutV2},
		{"2", LayoutV2},
		{"unknown", LayoutV1},
		{"", LayoutV1},
	}
	for _, c := range cases {
		got := ParseLayout(c.in)
		if got != c.want {
			t.Errorf("ParseLayout(%q) = %q, want %q", c.in, got, c.want)
		}
	}
}

func TestNewBuilderAutoDetectV1(t *testing.T) {
	tmpDir := t.TempDir()
	if err := os.MkdirAll(filepath.Join(tmpDir, "packages", "opencode", "script"), 0755); err != nil {
		t.Fatalf("mkdir: %v", err)
	}
	if err := os.WriteFile(filepath.Join(tmpDir, "packages", "opencode", "package.json"), []byte("{}"), 0644); err != nil {
		t.Fatalf("write: %v", err)
	}
	if err := os.MkdirAll(filepath.Join(tmpDir, "packages", "script", "src"), 0755); err != nil {
		t.Fatalf("mkdir: %v", err)
	}
	if err := os.WriteFile(filepath.Join(tmpDir, "packages", "script", "src", "index.ts"), []byte(""), 0644); err != nil {
		t.Fatalf("write: %v", err)
	}

	t.Setenv("OPENCODE_SOURCE_DIR", tmpDir)
	b, err := NewBuilder()
	if err != nil {
		if strings.Contains(err.Error(), "未找到 Bun") {
			return
		}
		t.Fatalf("NewBuilder: %v", err)
	}
	if b.layout != LayoutV1 {
		t.Errorf("NewBuilder auto layout = %q, want %q", b.layout, LayoutV1)
	}
	if !strings.HasSuffix(b.buildDir, filepath.Join("packages", "opencode")) {
		t.Errorf("NewBuilder buildDir = %q, want suffix packages/opencode", b.buildDir)
	}
}

func TestNewBuilderAutoDetectV2(t *testing.T) {
	tmpDir := t.TempDir()
	if err := os.MkdirAll(filepath.Join(tmpDir, "packages", "cli", "script"), 0755); err != nil {
		t.Fatalf("mkdir: %v", err)
	}
	buildTS := `const requestedTarget = process.argv.find((arg) => arg.startsWith("--target="))?.slice("--target=".length)`
	if err := os.WriteFile(filepath.Join(tmpDir, "packages", "cli", "script", "build.ts"), []byte(buildTS), 0644); err != nil {
		t.Fatalf("write: %v", err)
	}
	if err := os.MkdirAll(filepath.Join(tmpDir, "packages", "script", "src"), 0755); err != nil {
		t.Fatalf("mkdir: %v", err)
	}
	if err := os.WriteFile(filepath.Join(tmpDir, "packages", "script", "src", "index.ts"), []byte(""), 0644); err != nil {
		t.Fatalf("write: %v", err)
	}

	t.Setenv("OPENCODE_SOURCE_DIR", tmpDir)
	b, err := NewBuilder()
	if err != nil {
		if strings.Contains(err.Error(), "未找到 Bun") {
			t.Skip("bun not installed")
		}
		t.Fatalf("NewBuilder: %v", err)
	}
	if b.layout != LayoutV2 {
		t.Errorf("NewBuilder auto layout = %q, want %q", b.layout, LayoutV2)
	}
	if !strings.HasSuffix(b.buildDir, filepath.Join("packages", "cli")) {
		t.Errorf("NewBuilder buildDir = %q, want suffix packages/cli", b.buildDir)
	}
}

func TestGetDistPathV1V2(t *testing.T) {
	tmpDir := t.TempDir()
	cases := []struct {
		layout   Layout
		platform string
		bin      string
	}{
		{LayoutV1, "linux-x64", "opencode"},
		{LayoutV2, "linux-x64", "opencode"},
		{LayoutV2, "windows-x64", "opencode.exe"},
		{LayoutV1, "windows-x64", "opencode.exe"},
	}
	for _, c := range cases {
		buildDir := filepath.Join(tmpDir, string(c.layout))
		b := &Builder{buildDir: buildDir, layout: c.layout}
		subdir := "opencode-" + c.platform
		if c.layout == LayoutV2 {
			// 上游 build.ts: name = targetName(item).replace("opencode","cli")
			subdir = "cli-" + c.platform
		}
		want := filepath.Join(buildDir, "dist", subdir, "bin", c.bin)
		got := b.GetDistPath(c.platform)
		if got != want {
			t.Errorf("[%s %s] GetDistPath = %q, want %q", c.layout, c.platform, got, want)
		}
	}
}

func TestSourceVersion(t *testing.T) {
	tmpDir := t.TempDir()
	if err := os.WriteFile(filepath.Join(tmpDir, "package.json"), []byte(`{"name":"x","version":"2.0.12"}`), 0644); err != nil {
		t.Fatalf("write: %v", err)
	}
	b := &Builder{buildDir: tmpDir}
	if got := b.sourceVersion(); got != "2.0.12" {
		t.Errorf("sourceVersion = %q, want %q", got, "2.0.12")
	}

	// 缺 package.json 时返回空字符串（调用方跳过设置 OPENCODE_VERSION）
	empty := &Builder{buildDir: filepath.Join(tmpDir, "missing")}
	if got := empty.sourceVersion(); got != "" {
		t.Errorf("sourceVersion(missing) = %q, want empty", got)
	}
}

func TestV1RegressionBuildArgs(t *testing.T) {
	tmpDir := t.TempDir()
	if err := os.MkdirAll(filepath.Join(tmpDir, "packages", "opencode", "script"), 0755); err != nil {
		t.Fatalf("mkdir: %v", err)
	}
	if err := os.WriteFile(filepath.Join(tmpDir, "packages", "opencode", "package.json"), []byte("{}"), 0644); err != nil {
		t.Fatalf("write: %v", err)
	}
	if err := os.WriteFile(filepath.Join(tmpDir, "packages", "opencode", "script", "build.ts"), []byte(""), 0644); err != nil {
		t.Fatalf("write: %v", err)
	}
	if err := os.MkdirAll(filepath.Join(tmpDir, "packages", "script", "src"), 0755); err != nil {
		t.Fatalf("mkdir: %v", err)
	}
	if err := os.WriteFile(filepath.Join(tmpDir, "packages", "script", "src", "index.ts"), []byte(""), 0644); err != nil {
		t.Fatalf("write: %v", err)
	}

	l := detectLayout(tmpDir)
	if l != LayoutV1 {
		t.Fatalf("detectLayout = %q, want %q", l, LayoutV1)
	}
	b := &Builder{
		buildDir: filepath.Join(tmpDir, "packages", "opencode"),
		layout:   LayoutV1,
	}

	args := b.BuildArgs("linux-x64")
	want := []string{"run", "script/build.ts", "--single"}
	if len(args) != len(want) {
		t.Fatalf("V1 linux-x64 args = %v, want %v", args, want)
	}
	for i := range want {
		if args[i] != want[i] {
			t.Fatalf("V1 linux-x64 args[%d] = %q, want %q", i, args[i], want[i])
		}
	}
	t.Logf("V1 linux-x64 build args: %v", args)
}

func TestV2ArgsDrill(t *testing.T) {
	tmpDir := t.TempDir()
	if err := os.MkdirAll(filepath.Join(tmpDir, "packages", "cli", "script"), 0755); err != nil {
		t.Fatalf("mkdir: %v", err)
	}
	buildTS := `const requestedTarget = process.argv.find((arg) => arg.startsWith("--target="))?.slice("--target=".length)`
	if err := os.WriteFile(filepath.Join(tmpDir, "packages", "cli", "script", "build.ts"), []byte(buildTS), 0644); err != nil {
		t.Fatalf("write: %v", err)
	}
	if err := os.MkdirAll(filepath.Join(tmpDir, "packages", "script", "src"), 0755); err != nil {
		t.Fatalf("mkdir: %v", err)
	}
	if err := os.WriteFile(filepath.Join(tmpDir, "packages", "script", "src", "index.ts"), []byte(""), 0644); err != nil {
		t.Fatalf("write: %v", err)
	}

	l := detectLayout(tmpDir)
	if l != LayoutV2 {
		t.Fatalf("detectLayout = %q, want %q", l, LayoutV2)
	}
	b := &Builder{
		buildDir: filepath.Join(tmpDir, "packages", "cli"),
		layout:   LayoutV2,
	}

	args := b.BuildArgs("linux-x64")
	want := []string{"run", "script/build.ts", "--target=opencode-linux-x64", "--outdir=dist"}
	if len(args) != len(want) {
		t.Fatalf("V2 args = %v, want %v", args, want)
	}
	for i := range want {
		if args[i] != want[i] {
			t.Fatalf("V2 args[%d] = %q, want %q", i, args[i], want[i])
		}
	}
	t.Logf("V2 linux-x64 build args: %v", args)
}

func TestV1RealSourceLayout(t *testing.T) {
	realSrc := "/tmp/oc-dev-v1"
	if !DirExists(filepath.Join(realSrc, "packages", "opencode")) {
		t.Skipf("V1 real source not found at %s", realSrc)
	}
	t.Setenv("OPENCODE_SOURCE_DIR", realSrc)
	b, err := NewBuilder()
	if err != nil {
		if strings.Contains(err.Error(), "未找到 Bun") {
			b = &Builder{buildDir: filepath.Join(realSrc, "packages", "opencode"), layout: LayoutV1}
		} else {
			t.Fatalf("NewBuilder: %v", err)
		}
	}
	if b.layout != LayoutV1 {
		t.Fatalf("real V1 source layout = %q, want %q", b.layout, LayoutV1)
	}
	args := b.BuildArgs("linux-x64")
	want := []string{"run", "script/build.ts", "--single"}
	if len(args) != len(want) {
		t.Fatalf("V1 real args = %v, want %v", args, want)
	}
	t.Logf("V1 real source (%s) build args: %v", realSrc, args)
}

func TestV2RealSourceLayout(t *testing.T) {
	realSrc := "/tmp/oc-v2012"
	if !DirExists(filepath.Join(realSrc, "packages", "cli")) {
		t.Skipf("V2 real source not found at %s", realSrc)
	}
	t.Setenv("OPENCODE_SOURCE_DIR", realSrc)
	b, err := NewBuilder()
	if err != nil {
		if strings.Contains(err.Error(), "未找到 Bun") {
			b = &Builder{buildDir: filepath.Join(realSrc, "packages", "cli"), layout: LayoutV2}
		} else {
			t.Fatalf("NewBuilder: %v", err)
		}
	}
	if b.layout != LayoutV2 {
		t.Fatalf("real V2 source layout = %q, want %q", b.layout, LayoutV2)
	}
	args := b.BuildArgs("linux-x64")
	want := []string{"run", "script/build.ts", "--target=opencode-linux-x64", "--outdir=dist"}
	if len(args) != len(want) {
		t.Fatalf("V2 real args = %v, want %v", args, want)
	}
	t.Logf("V2 real source (%s) build args: %v", realSrc, args)
}
