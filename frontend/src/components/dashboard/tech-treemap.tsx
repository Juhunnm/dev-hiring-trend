import { getStats } from "@/api/dashboard";
import { useQuery } from "@tanstack/react-query";
import { ResponsiveContainer, Treemap } from "recharts";

const COLORS = [
  "var(--chart-1)",
  "var(--chart-2)",
  "var(--chart-3)",
  "var(--chart-4)",
  "var(--chart-5)",
];
const CustomContent = ({ x, y, width, height, index, name }) => (
  <g>
    <rect
      x={x}
      y={y}
      width={width}
      height={height}
      fill={COLORS[index % COLORS.length]} // ← index 순서대로 색상
      stroke="var(--background)"
    />
    <text
      x={x + width / 2}
      y={y + height / 2}
      textAnchor="middle"
      fill="var(--foreground)"
      fontSize={12}
    >
      {name}
    </text>
  </g>
);
export default function TechTreemap({ selectedRole }) {
  const { data, isPending } = useQuery({
    queryKey: ["stats", selectedRole],
    queryFn: () => getStats(selectedRole),
  });

  return (
    <ResponsiveContainer width="100%" height={400}>
      <Treemap
        data={data}
        dataKey="count"
        nameKey="tech"
        content={<CustomContent />}
        // stroke="var(--background)"
        // fill="var(--chart-1)"
      />
    </ResponsiveContainer>
  );
}
