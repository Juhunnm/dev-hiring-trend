import { Route, Routes } from "react-router-dom";
import IndexPage from "./page/index-page";
import GlobalLayout from "./components/layout/global-layout";

export default function RootRoute() {
  return (
    <Routes>
      <Route element={<GlobalLayout />}>
        <Route path="/" element={<IndexPage />} />
      </Route>
    </Routes>
  );
}
