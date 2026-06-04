import { describe, it, expect, vi } from "vitest";

const mockCreateRef = vi.fn().mockResolvedValue({});
const mockGetContent = vi.fn().mockRejectedValue({ status: 404 });
const mockCreateOrUpdateFileContents = vi.fn().mockResolvedValue({});
const mockCreate = vi.fn().mockResolvedValue({ data: { number: 103, html_url: "https://github.com/testorg/testrepo/pull/103" } });

const mockOctokit = {
  git: { getRef: vi.fn().mockResolvedValue({ data: { object: { sha: "abc123" } } }), createRef: mockCreateRef },
  repos: { getContent: mockGetContent, createOrUpdateFileContents: mockCreateOrUpdateFileContents },
  pulls: { create: mockCreate },
};

describe("createDocPR", () => {
  it("creates a branch with the correct name and opens a PR with the correct title", async () => {
    const { createDocPR } = await import("../github/pr.js");

    const result = await createDocPR(
      mockOctokit as never,
      "testorg",
      "testrepo",
      42,
      [{ path: "CHANGELOG.md", content: "## Added\n- Auth" }],
      "Doc PR body"
    );

    expect(mockCreateRef).toHaveBeenCalledWith(
      expect.objectContaining({ ref: "refs/heads/devlogai/docs-pr-42" })
    );
    expect(mockCreate).toHaveBeenCalledWith(
      expect.objectContaining({ title: "docs: update documentation for merged PR #42" })
    );
    expect(result.number).toBe(103);
  });
});
