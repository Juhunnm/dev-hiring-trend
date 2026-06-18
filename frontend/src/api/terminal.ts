export async function getJobs() {
  const res = await fetch(`${import.meta.env.VITE_API_URL}/jobs`);
  return res.json();
}
