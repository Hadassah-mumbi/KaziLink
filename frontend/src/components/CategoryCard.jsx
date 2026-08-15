import { Link } from "react-router-dom";
import {
  Baby, Wrench, Sparkles, Trees, Droplets, Hammer, Zap, PaintRoller, BrickWall,
  BriefcaseBusiness
} from "lucide-react";

const iconMap = {
  nanny: Baby,
  househelp: Sparkles,
  "house manager": BriefcaseBusiness,
  cleaner: Sparkles,
  gardener: Trees,
  plumber: Droplets,
  carpenter: Hammer,
  electrician: Zap,
  mechanic: Wrench,
  painter: PaintRoller,
  mason: BrickWall,
};

export default function CategoryCard({ category, compact = false }) {
  const Icon = iconMap[String(category.name).toLowerCase()] || BriefcaseBusiness;
  return (
    <Link to={`/providers?category=${category.id}`} className={`category-card ${compact ? "compact" : ""}`}>
      <div className="category-icon"><Icon size={compact ? 22 : 28} /></div>
      <span>{category.name}</span>
    </Link>
  );
}
