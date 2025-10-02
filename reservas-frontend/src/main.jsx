import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login.jsx";
import {ClientDashboard} from "./pages/client/ClientDashboard.jsx";
import AdminDashboard from "./pages/admin/AdminDashboard.jsx";
import StaffDashboard from "./pages/staff/StaffDashboard.jsx";

const Private = ({ children, roles }) => {
  const token = localStorage.getItem("rv_token");
  const role = localStorage.getItem("rv_role");
  if (!token) return <Navigate to="/login" replace />;
  if (roles && !roles.includes(role)) return <Navigate to="/login" replace />;
  return children;
};

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<Private roles={['CLIENT','ADMIN','STAFF']}><ClientDashboard/></Private>} />
        <Route path="/admin" element={<Private roles={['ADMIN']}><AdminDashboard/></Private>} />
        <Route path="/staff" element={<Private roles={['ADMIN','STAFF']}><StaffDashboard/></Private>} />
      </Routes>
    </BrowserRouter>
  );
}
