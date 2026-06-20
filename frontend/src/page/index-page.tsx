import Filter from "@/components/dashboard/filter";
import TechTreemap from "@/components/dashboard/tech-treemap";
import Terminal from "@/components/dashboard/terminal";
import TopSkillsTable from "@/components/dashboard/top-skills-table";

export default function IndexPage() {
  return (
    <div className="m-auto px-2 flex flex-col gap-3">
      <Terminal />
      {/* <Filter /> */}
      <TechTreemap />
      <TopSkillsTable />
    </div>
  );
}
