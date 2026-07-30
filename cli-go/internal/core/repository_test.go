package core

import "testing"

func TestReleaseRepositoryDefault(t *testing.T) {
	t.Setenv("OPENCODE_I18N_REPO", "")
	if got := ReleaseRepository(); got != DefaultReleaseRepository {
		t.Fatalf("ReleaseRepository() = %q, want %q", got, DefaultReleaseRepository)
	}
}

func TestReleaseRepositoryOverride(t *testing.T) {
	t.Setenv("OPENCODE_I18N_REPO", "example/opencode-zh")
	if got := ReleaseRepository(); got != "example/opencode-zh" {
		t.Fatalf("ReleaseRepository() = %q", got)
	}
}

func TestReleaseRepositoryRejectsInvalidOverride(t *testing.T) {
	t.Setenv("OPENCODE_I18N_REPO", "https://example.com/not-allowed")
	if got := ReleaseRepository(); got != DefaultReleaseRepository {
		t.Fatalf("invalid override should fall back, got %q", got)
	}
}
