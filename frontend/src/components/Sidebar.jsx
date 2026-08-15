import { NavLink } from "react-router-dom";
import {
  LayoutDashboard, CalendarDays, UserRound, BriefcaseBusiness, Clock3,
  Users, ShieldCheck, Settings
} from "lucide-react";

const customer = [
  ["/dashboard", "Dashboard", LayoutDashboard],
  ["/dashboard/bookings", "My bookings", CalendarDays],
  ["/dashboard/profile", "My profile", UserRound],
];

const provider = [
  ["/provider/dashboard", "Dashboard", LayoutDashboard],
  ["/provider/bookings", "Bookings", CalendarDays],
  ["/provider/profile", "My profile", UserRound],
  ["/provider/services", "My services", BriefcaseBusiness],
  ["/provider/availability", "Availability", Clock3],
];

const admin = [
  ["/admin/dashboard", "Dashboard", LayoutDashboard],
  ["/admin/providers", "Providers", ShieldCheck],
  ["/admin/users", "Users", Users],
];

export default function Sidebar({ type }) {
  const items = type === "admin" ? admin : type === "provider" ? provider : customer;

  return (
    <aside className="sidebar">
      <div className="sidebar-title">{type === "admin" ? "Admin" : type === "provider" ? "Provider" : "My KaziLink"}</div>
      {items.map(([to, label, Icon]) => (
        <NavLink key={to} to={to} end className={({ isActive }) => isActive ? "side-link active" : "side-link"}>
          <Icon size={18} /> {label}
        </NavLink>
      ))}
    </aside>
  );
}
