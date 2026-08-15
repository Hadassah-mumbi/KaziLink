import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import CategoryCard from "../components/CategoryCard";
import Loading from "../components/Loading";
import ErrorMessage from "../components/ErrorMessage";
import { getCategories } from "../api/categories";
import { getApiError } from "../api/axios";

export default function Categories() {
  const [categories, setCategories] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    getCategories().then(setCategories).catch((e) => setError(getApiError(e)));
  }, []);

  return (
    <>
      <Navbar />
      <main className="content-page">
        <div className="section-heading">
          <p className="eyebrow">Our services</p>
          <h1>All the help your home needs.</h1>
          <p>Choose a service to see approved providers who offer it.</p>
        </div>
        <ErrorMessage message={error} />
        {categories.length ? <div className="category-grid">{categories.map((c) => <CategoryCard key={c.id} category={c} />)}</div> : <Loading label="Loading services..." />}
      </main>
      <Footer />
    </>
  );
}
