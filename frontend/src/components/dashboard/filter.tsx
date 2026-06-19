import { getJobCategories } from "@/api/dashboard";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { useQuery } from "@tanstack/react-query";
import { Skeleton } from "../ui/skeleton";
import { useSelectedRole, useSetSelectedRole } from "@/store/dashboard";

export default function Filter() {
  const selectedRole = useSelectedRole();
  const setSelectedRole = useSetSelectedRole();

  const { data, isPending, error } = useQuery({
    queryKey: ["job-categories"],
    queryFn: getJobCategories,
  });

  if (error)
    return <div className="font-mono text-red-400">error: {error.message}</div>;

  return (
    <div className="flex items-center font-mono text-sm">
      <span className="text-green-400">&gt;</span>
      <span className="text-muted-foreground">&nbsp;--role&nbsp;</span>

      <ToggleGroup
        className="px-1 py-2 "
        type="single"
        size="sm"
        defaultValue="all"
        variant="outline"
        spacing={2}
        value={selectedRole}
        onValueChange={(v) => {
          if (v) setSelectedRole(v);
        }}
      >
        {isPending ? (
          Array(5)
            .fill(0)
            .map((_, i) => <Skeleton key={i} className="w-16 h-7 rounded" />)
        ) : (
          <>
            <ToggleGroupItem className="cursor-pointer" value="all">
              All
            </ToggleGroupItem>
            {data?.map((f) => (
              <ToggleGroupItem className="cursor-pointer" key={f} value={f}>
                {f}
              </ToggleGroupItem>
            ))}
          </>
        )}
      </ToggleGroup>
    </div>
  );
}
