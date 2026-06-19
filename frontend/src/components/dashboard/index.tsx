import { useState } from "react";
import Filter from "./filter";
import TechTreemap from "./tech-treemap";
import TopSkillsTable from "./top-skills-table";

export default function Dashboard() {
  const [selectedRole, setSelectedRole] = useState("all");

  return (
    <div>
      <Filter selectedRole={selectedRole} onRoleChange={setSelectedRole} />
      {/* 나중에 추가 */}
      <TechTreemap selectedRole={selectedRole} />
      <TopSkillsTable selectedRole={selectedRole} />
    </div>
  );
}
