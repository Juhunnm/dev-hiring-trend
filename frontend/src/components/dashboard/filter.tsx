import { getJobCategories } from "@/api/dashboard";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { useQuery } from "@tanstack/react-query";
import { Skeleton } from "../ui/skeleton";

export default function Filter({ selectedRole, onRoleChange }) {
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
        className="px-1 py-2"
        type="single"
        size="sm"
        defaultValue="all"
        variant="outline"
        spacing={2}
        onValueChange={(v) => {
          if (v) onRoleChange(v);
        }}
      >
        {isPending ? (
          Array(5)
            .fill(0)
            .map((_, i) => <Skeleton key={i} className="w-16 h-7 rounded" />)
        ) : (
          <>
            <ToggleGroupItem value="all">All</ToggleGroupItem>
            {data?.map((f) => (
              <ToggleGroupItem key={f} value={f}>
                {f}
              </ToggleGroupItem>
            ))}
          </>
        )}
      </ToggleGroup>
    </div>
  );
}
