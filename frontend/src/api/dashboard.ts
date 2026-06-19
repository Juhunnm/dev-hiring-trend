export async function getJobIndexes() {
  const res = await fetch(`${import.meta.env.VITE_API_URL}/jobs`);
  return res.json();
}

export async function getJobCategories() {
  const res = await fetch(`${import.meta.env.VITE_API_URL}/job-categories`);
  return res.json();
}

export async function getStats(jobName?: string) {
  const url =
    jobName && jobName !== "all"
      ? `${import.meta.env.VITE_API_URL}/stats?job_name=${jobName}`
      : `${import.meta.env.VITE_API_URL}/stats`;

  const res = await fetch(url);
  return res.json();
}
