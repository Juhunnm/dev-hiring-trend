import { getStats } from "@/api/dashboard";
import { useSelectedRole } from "@/store/dashboard";
import { useQuery } from "@tanstack/react-query";
import { ResponsiveContainer, Treemap } from "recharts";

const COLORS = ["#39D353", "#26A641", "#006D32", "#0E4429", "#161B22"];
const getColor = (count: number, maxCount: number) => {
  const ratio = count / maxCount; // 0 ~ 1 사이 값

  // ratio가 클수록 밝은 초록, 작을수록 어두운 초록
  if (ratio > 0.8) return "#39D353";
  if (ratio > 0.6) return "#26A641";
  if (ratio > 0.4) return "#006D32";
  if (ratio > 0.2) return "#0E4429";
  return "#161B22";
};
const CustomContent = ({ x, y, width, height, name, value, root }) => {
  const maxCount = root?.children?.[0]?.value ?? value;
  const color = getColor(value, maxCount);

  return (
    <g>
      <rect
        x={x}
        y={y}
        width={width}
        height={height}
        fill={color}
        stroke="var(--background)"
      />
      {width > 40 && height > 20 && (
        <text
          x={x + width / 2}
          y={y + height / 2}
          textAnchor="middle"
          fill="white"
          fontSize={12}
        >
          {name}
        </text>
      )}
    </g>
  );
};
export default function TechTreemap() {
  const selectedRole = useSelectedRole();

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
        isAnimationActive={false}
      />
    </ResponsiveContainer>
  );
}
