import { getJobIndexes } from "@/api/dashboard";
import { Card, CardContent } from "@/components/ui/card";
import { useQuery } from "@tanstack/react-query";
import Filter from "./filter";
import { useSelectedRole } from "@/store/dashboard";
// import { useEffect, useState } from "react";

export default function Terminal() {
  const selectedRole = useSelectedRole();
  const { data, isPending, error } = useQuery({
    queryKey: ["job_index"],
    queryFn: getJobIndexes,
  });
  return (
    <Card className="font-mono">
      <CardContent className="px-4 py-2 space-y-1">
        <div className="flex gap-2 text-sm">
          <span className="text-green-400">$</span>
          <span>fetch</span>
          <span className="text-muted-foreground">--role={selectedRole}</span>
        </div>
        <div className="ml-5">
          <div className="flex gap-2 text-sm ">
            <span className="text-green-400">&gt;</span>
            {isPending ? (
              <span className="text-green-400">데이터 수집 중 ...</span>
            ) : error ? (
              <span className="text-red-400">오류 발생 {error.message}</span>
            ) : (
              <span className="text-green-400">
                {data?.length.toLocaleString()}개 채용공고에서 기술 스택 데이터
                수집 완료
              </span>
            )}
          </div>

          {/* 메타 정보 */}
          <div className="text-muted-foreground text-xs">
            last updated: 2026. 6. 17. | source: saramin
          </div>
        </div>
        {/* filter */}
        <Filter />
      </CardContent>
    </Card>
  );
}
