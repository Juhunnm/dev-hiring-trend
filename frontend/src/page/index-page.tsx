import Filter from "@/components/dashboard/filter";
import Terminal from "@/components/dashboard/terminal";

export default function IndexPage() {
  return (
    <div className="m-auto px-2">
      <Terminal />
      <Filter />
    </div>
  );
}
