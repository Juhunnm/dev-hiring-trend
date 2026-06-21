import { getStats } from "@/api/dashboard";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useQuery } from "@tanstack/react-query";
import { Skeleton } from "../ui/skeleton";
import { useSelectedRole } from "@/store/dashboard";

export default function TopSkillsTable() {
  const selectedRole = useSelectedRole();

  const { data, isPending } = useQuery({
    queryKey: ["stats", selectedRole],
    queryFn: () => getStats(selectedRole),
  });
  return (
    <div className="font-mono">
      <div className="text-muted-foreground text-xs mb-2">
        top_10_skills.json
      </div>

      <div className="max-h-[400px] overflow-y-auto border rounded-md">
        <Table className="felx flex-col">
          <TableHeader className="sticky top-0 border-b backdrop-blur-sm bg-background/25   ">
            <TableRow>
              <TableHead className="w-[100px]">#</TableHead>
              <TableHead>skill_name</TableHead>
              <TableHead>category</TableHead>
              <TableHead>count</TableHead>
              <TableHead>grow</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isPending
              ? Array(10)
                  .fill(0)
                  .map((_, i) => (
                    // colSpan={5}
                    <TableRow key={i}>
                      <TableCell>
                        <Skeleton className="h-4 w-full" />
                      </TableCell>
                      <TableCell>
                        <Skeleton className="h-4 w-full" />
                      </TableCell>
                      <TableCell>
                        <Skeleton className="h-4 w-full" />
                      </TableCell>
                      <TableCell>
                        <Skeleton className="h-4 w-full" />
                      </TableCell>
                      <TableCell>
                        <Skeleton className="h-4 w-full" />
                      </TableCell>
                    </TableRow>
                  ))
              : data?.map((d, index) => (
                  <TableRow key={d.tech}>
                    <TableCell className="font-medium">
                      {String(index + 1).padStart(2, "0")}
                    </TableCell>
                    <TableCell>{d.tech}</TableCell>
                    <TableCell>category</TableCell>
                    <TableCell>{d.count.toLocaleString()}</TableCell>
                    <TableCell>grow</TableCell>
                  </TableRow>
                ))}
          </TableBody>
          <TableCaption className="text-xs">
            {isPending ? "loading..." : `total ${data?.length} skills found`}
          </TableCaption>
        </Table>
      </div>
    </div>
  );
}
