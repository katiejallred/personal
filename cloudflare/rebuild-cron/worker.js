// Cloudflare Worker that starts the site's GitHub Pages deploy on a timer.
//
// GitHub's own scheduled runs are often hours late (or skipped) when Actions
// is busy, so scheduled posts went live late. Cloudflare's cron triggers fire
// on time; this Worker asks GitHub to run .github/workflows/pages.yml, the
// same as clicking "Run workflow" on the Actions tab.
//
// Settings (Worker → Settings → Variables and Secrets):
//   GITHUB_TOKEN  secret: fine-grained token for katiejallred/personal with
//                 "Actions: Read and write" and nothing else
//   REPO          optional, default "katiejallred/personal"
//   WORKFLOW      optional, default "pages.yml"
//   BRANCH        optional, default "main"
// Trigger: a cron trigger, e.g. "5 * * * *" (five past every hour, UTC).
// Setup steps are in MAINTAINING.md under "Deploying".

export default {
  async scheduled(controller, env, ctx) {
    ctx.waitUntil(startDeploy(env));
  },

  // The Worker has no public page; visiting its URL just says so.
  async fetch() {
    return new Response("Not found", { status: 404 });
  },
};

export async function startDeploy(env, fetchImpl = fetch) {
  if (!env.GITHUB_TOKEN) throw new Error("GITHUB_TOKEN secret is not set");

  const repo = env.REPO || "katiejallred/personal";
  const workflow = env.WORKFLOW || "pages.yml";
  const url = `https://api.github.com/repos/${repo}/actions/workflows/${workflow}/dispatches`;

  const res = await fetchImpl(url, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${env.GITHUB_TOKEN}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "User-Agent": "katieallred-rebuild-cron",
    },
    body: JSON.stringify({ ref: env.BRANCH || "main" }),
  });

  // GitHub answers 204 No Content when the run is queued.
  if (res.status !== 204) {
    throw new Error(`GitHub refused the deploy: ${res.status} ${await res.text()}`);
  }
}
