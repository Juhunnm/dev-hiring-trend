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
export async function getLastUpdated() {
  const res = await fetch(`${import.meta.env.VITE_API_URL}/last-updated`);

  if (!res.ok) {
    throw new Error("last_updated 조회 실패");
  }

  const data = await res.json();

  if (!data.last_updated) {
    throw new Error("last_updated 데이터 없음");
  }
  return {
    last_updated: new Date(data.last_updated).toLocaleDateString("ko-KR"),
  };
}
