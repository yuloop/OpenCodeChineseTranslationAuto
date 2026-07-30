package core

import (
	"os"
	"regexp"
)

const DefaultReleaseRepository = "yuloop/OpenCodeChineseTranslationAuto"

var repositoryPattern = regexp.MustCompile(`^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$`)

// ReleaseRepository returns the GitHub repository used for release downloads.
// Fork maintainers can override it without recompiling by setting
// OPENCODE_I18N_REPO=owner/repository.
func ReleaseRepository() string {
	value := os.Getenv("OPENCODE_I18N_REPO")
	if repositoryPattern.MatchString(value) {
		return value
	}
	return DefaultReleaseRepository
}

func ReleaseRepositoryURL() string {
	return "https://github.com/" + ReleaseRepository()
}

func LatestReleaseAPIURL() string {
	return "https://api.github.com/repos/" + ReleaseRepository() + "/releases/latest"
}
