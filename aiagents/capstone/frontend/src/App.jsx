import { Navigate, Route, Routes } from "react-router-dom";

import Desk from "./pages/Desk.jsx";
import Landing from "./pages/Landing.jsx";
import Queue from "./pages/Queue.jsx";
import TicketPage from "./pages/TicketPage.jsx";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/desk" element={<Desk />} />
      <Route path="/team" element={<Queue />} />
      <Route path="/team/:ticketId" element={<TicketPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
