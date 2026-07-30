import { workflow, type LibrettoWorkflowContext } from "libretto";
import { z } from "zod";

const repositoryPart = z
  .string()
  .min(1)
  .max(100)
  .regex(/^[A-Za-z0-9_.-]+$/, "must be a GitHub owner or repository name");

const inputSchema = z.object({
  owner: repositoryPart,
  repository: repositoryPart,
});

const outputSchema = z.object({
  exists: z.literal(true),
  publicUrl: z.string().url(),
  pageTitle: z.string().min(1),
});

export default workflow("verifyGitHubRepository", {
  input: inputSchema,
  output: outputSchema,
  handler: async (ctx: LibrettoWorkflowContext, input) => {
    const { page, session } = ctx;
    const publicUrl = `https://github.com/${input.owner}/${input.repository}`;

    console.log("repository-verification-start", { session, publicUrl });
    const response = await page.goto(publicUrl, { waitUntil: "domcontentloaded" });
    if (!response || response.status() >= 400) {
      throw new Error(`GitHub repository is not publicly reachable: HTTP ${response?.status() ?? "unknown"}`);
    }

    await page.getByRole("main").waitFor({ state: "visible" });
    const repositoryLink = page.getByRole("link", { name: input.repository, exact: true }).first();
    if (!(await repositoryLink.isVisible())) {
      throw new Error(`GitHub repository identity was not visible at ${publicUrl}`);
    }

    const pageTitle = await page.title();
    console.log("repository-verification-complete", { publicUrl, pageTitle });
    return { exists: true as const, publicUrl, pageTitle };
  },
});
