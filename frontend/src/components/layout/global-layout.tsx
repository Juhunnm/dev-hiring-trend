import { Outlet } from "react-router-dom";

export default function GlobalLayout() {
  return (
    <div className=" flex flex-col min-h-[100vh]">
      <header className="h-15 border-b">
        <div className="m-auto flex h-full w-full  justify-between px-4">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-red-500" />
            <div className="w-4 h-4 rounded-full bg-yellow-500" />
            <div className="w-4 h-4 rounded-full bg-green-500" />
            <div className="flex gap-2 items-center">
              <div className="text-green-400">$</div>
              <div className="text-muted-foreground">dev hiring trend</div>
              <div className="w-2 h-4 bg-green-400 animate-caret-blink" />{" "}
            </div>
          </div>
          <div className="text-muted-foreground flex items-center gap-3 text-sm">
            <div>v1.0.0</div>
          </div>
        </div>
      </header>
      <main className="m-auto w-full flex-1 px-2 py-4">
        <Outlet />
      </main>
      <footer>
        <div>updated 2026-06-16 14:02 KST</div>
      </footer>
    </div>
  );
}
