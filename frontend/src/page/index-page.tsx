import TechTreemap from "@/components/dashboard/tech-treemap";
import Terminal from "@/components/dashboard/terminal";
import TopSkillsTable from "@/components/dashboard/top-skills-table";

export default function IndexPage() {
  return (
    <div className="m-auto px-2 flex flex-col gap-3 ">
      <Terminal />
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-2">
        <TechTreemap />
        <TopSkillsTable />
      </div>
    </div>
  );
}
