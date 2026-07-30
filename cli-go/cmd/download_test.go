package cmd

import (
	"crypto/sha256"
	"encoding/hex"
	"os"
	"path/filepath"
	"testing"
)

func TestVerifyAssetDigest(t *testing.T) {
	path := filepath.Join(t.TempDir(), "asset.zip")
	content := []byte("verified release asset")
	if err := os.WriteFile(path, content, 0o644); err != nil {
		t.Fatal(err)
	}

	sum := sha256.Sum256(content)
	digest := "sha256:" + hex.EncodeToString(sum[:])
	if err := verifyAssetDigest(path, digest); err != nil {
		t.Fatalf("valid digest rejected: %v", err)
	}
}

func TestVerifyAssetDigestRejectsMismatch(t *testing.T) {
	path := filepath.Join(t.TempDir(), "asset.zip")
	if err := os.WriteFile(path, []byte("tampered"), 0o644); err != nil {
		t.Fatal(err)
	}

	err := verifyAssetDigest(path, "sha256:"+string(make([]byte, sha256.Size*2)))
	if err == nil {
		t.Fatal("expected digest mismatch")
	}
}
