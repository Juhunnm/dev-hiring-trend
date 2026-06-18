import { getJobs } from "@/api/terminal";
import { Card, CardContent } from "@/components/ui/card";
import { useEffect, useState } from "react";

export default function Terminal() {
  const [totalJobs, setTotalJobs] = useState(0);

  useEffect(() => {
    const fetchData = async () => {
      const jobs = await getJobs();
      setTotalJobs(jobs.length);
    };
    fetchData();
  }, []);

  return (
    <Card className="font-mono">
      <CardContent className="p-4 space-y-1">
        <div className="flex gap-2 text-sm">
          <span className="text-green-400">$</span>
          <span className="">fetch</span>
          {/* <span className="text-muted-foreground">
            --source=job_postings --analyze=tech_stack
          </span> */}
        </div>
        <div className="ml-5">
          <div className="flex gap-2 text-sm ">
            <span className="text-green-400">&gt;</span>
            <span className="text-green-400">
              {totalJobs.toLocaleString()}개 채용공고에서 기술 스택 데이터 수집
              완료
            </span>
          </div>

          {/* 메타 정보 */}
          <div className="text-muted-foreground text-xs">
            last updated: 2026. 6. 17. | source: saramin
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
