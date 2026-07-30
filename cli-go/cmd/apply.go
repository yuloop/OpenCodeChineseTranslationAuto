package cmd

import (
	"fmt"
	"opencode-cli/internal/core"

	"github.com/spf13/cobra"
)

var applyCmd = &cobra.Command{
	Use:   "apply",
	Short: "应用汉化补丁到源码",
	RunE: func(cmd *cobra.Command, args []string) error {
		dryRun, _ := cmd.Flags().GetBool("dry-run")
		silent, _ := cmd.Flags().GetBool("silent")
		strict, _ := cmd.Flags().GetBool("strict")
		minMatchRate, _ := cmd.Flags().GetFloat64("min-match-rate")

		if minMatchRate < 0 || minMatchRate > 1 {
			return fmt.Errorf("--min-match-rate 必须在 0 到 1 之间")
		}

		return runApply(dryRun, silent, strict, minMatchRate)
	},
}

func runApply(dryRun, silent, strict bool, minMatchRate float64) error {
	i18n, err := core.NewI18n()
	if err != nil {
		return fmt.Errorf("初始化失败: %w", err)
	}

	configs, err := i18n.LoadConfig()
	if err != nil {
		return fmt.Errorf("加载配置失败: %w", err)
	}

	if !silent {
		if dryRun {
			fmt.Println("模拟应用汉化配置...")
		} else {
			fmt.Println("应用汉化配置...")
		}
		fmt.Printf("找到 %d 个配置文件\n", len(configs))
	}

	stats := struct {
		Files struct {
			Total   int
			Success int
			Skipped int
			Failed  int
		}
		Replacements struct {
			Total   int
			Success int
			Failed  int
		}
	}{}

	results := i18n.ApplyConfigs(configs, dryRun)
	for index, config := range configs {
		result := results[index]

		stats.Files.Total++
		if result.Skipped {
			stats.Files.Skipped++
			if !silent && result.Replacements.Total > 0 {
				fmt.Printf("  ⚠ %s 跳过: %s\n", config.File, result.SkipReason)
			}
		} else if result.Success {
			stats.Files.Success++
			if !silent {
				fmt.Printf("  ✓ %s (%d/%d 处替换)\n", config.File, result.Replacements.Success, result.Replacements.Total)
			}
		} else {
			stats.Files.Failed++
			if !silent {
				fmt.Printf("  ✗ %s 失败\n", config.File)
			}
		}

		stats.Replacements.Total += result.Replacements.Total
		stats.Replacements.Success += result.Replacements.Success
		stats.Replacements.Failed += result.Replacements.Failed
	}

	matchRate := 1.0
	if stats.Replacements.Total > 0 {
		matchRate = float64(stats.Replacements.Success) / float64(stats.Replacements.Total)
	}

	if !silent {
		fmt.Println("")
		if dryRun {
			fmt.Println("汉化模拟完成:")
		} else {
			fmt.Println("汉化应用完成:")
		}
		fmt.Printf("  📁 文件: %d 成功, %d 跳过, %d 失败\n", stats.Files.Success, stats.Files.Skipped, stats.Files.Failed)
		fmt.Printf("  📝 替换: %d/%d 成功 (%.1f%%)\n", stats.Replacements.Success, stats.Replacements.Total, matchRate*100)
	}

	if strict && (stats.Files.Failed > 0 || matchRate < minMatchRate) {
		return fmt.Errorf(
			"汉化质量门禁未通过: 匹配率 %.1f%%，要求至少 %.1f%%，失败文件 %d",
			matchRate*100,
			minMatchRate*100,
			stats.Files.Failed,
		)
	}

	return nil
}

func init() {
	rootCmd.AddCommand(applyCmd)
	applyCmd.Flags().Bool("dry-run", false, "Simulate the application without modifying files")
	applyCmd.Flags().Bool("silent", false, "Suppress output")
	applyCmd.Flags().Bool("strict", false, "Fail when translation coverage is below the required match rate")
	applyCmd.Flags().Float64("min-match-rate", 1.0, "Required translation match rate in strict mode (0.0-1.0)")
}
