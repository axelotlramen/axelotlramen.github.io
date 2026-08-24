import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Layout } from "@/components/layout/Layout";
import { Home } from "@/pages/Home";
import { Hsr } from "@/pages/Hsr";
import { Genshin } from "@/pages/Genshin";
import { Endfield } from "@/pages/Endfield";
import { Endgame } from "@/pages/Endgame";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="hsr" element={<Hsr />} />
          <Route path="genshin" element={<Genshin />} />
          <Route path="endfield" element={<Endfield />} />
          <Route path="endgame" element={<Endgame />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
