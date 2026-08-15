import { Routes, Route } from "react-router-dom";

import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Categories from "./pages/Categories";
import Providers from "./pages/Providers";
import ProviderDetails from "./pages/ProviderDetails";
import BookProvider from "./pages/BookProvider";
import BecomeProvider from "./pages/BecomeProvider";
import DashboardChooser from "./pages/DashboardChooser";

import ProtectedRoute from "./components/ProtectedRoute";

// Customer pages
import CustomerDashboard from "./pages/customer/Dashboard";
import CustomerBookings from "./pages/customer/Bookings";
import CustomerBookingDetails from "./pages/customer/BookingDetails";
import CustomerReview from "./pages/customer/ReviewProvider";
import CustomerProfile from "./pages/customer/Profile";

// Provider pages
import ProviderDashboard from "./pages/provider/Dashboard";
import ProviderProfile from "./pages/provider/Profile";
import ProviderServices from "./pages/provider/Services";
import ProviderAvailability from "./pages/provider/Availability";
import ProviderBookings from "./pages/provider/Bookings";
import ProviderBookingDetails from "./pages/provider/BookingDetails";

// Admin pages
import AdminDashboard from "./pages/admin/Dashboard";
import AdminProviders from "./pages/admin/Providers";
import AdminProviderDetails from "./pages/admin/ProviderDetails";
import AdminUsers from "./pages/admin/Users";

export default function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/categories" element={<Categories />} />
      <Route path="/providers" element={<Providers />} />
      <Route path="/providers/:providerId" element={<ProviderDetails />} />
      <Route
        path="/providers/:providerId/book"
        element={<BookProvider />}
      />
      <Route path="/become-provider" element={<BecomeProvider />} />
      <Route path="/dashboard/choose" element={<DashboardChooser />} />

      {/* Customer routes */}
      <Route element={<ProtectedRoute role="customer" />}>
        <Route path="/dashboard" element={<CustomerDashboard />} />
        <Route path="/dashboard/profile" element={<CustomerProfile />} />
        <Route path="/dashboard/bookings" element={<CustomerBookings />} />
        <Route
          path="/dashboard/bookings/:bookingId"
          element={<CustomerBookingDetails />}
        />
        <Route
          path="/dashboard/bookings/:bookingId/review"
          element={<CustomerReview />}
        />
      </Route>

      {/* Provider routes */}
      <Route element={<ProtectedRoute role="provider" />}>
        <Route path="/provider/dashboard" element={<ProviderDashboard />} />
        <Route path="/provider/profile" element={<ProviderProfile />} />
        <Route path="/provider/services" element={<ProviderServices />} />
        <Route
          path="/provider/availability"
          element={<ProviderAvailability />}
        />
        <Route path="/provider/bookings" element={<ProviderBookings />} />
        <Route
          path="/provider/bookings/:bookingId"
          element={<ProviderBookingDetails />}
        />
      </Route>

      {/* Admin routes */}
      <Route element={<ProtectedRoute role="admin" />}>
        <Route path="/admin/dashboard" element={<AdminDashboard />} />
        <Route path="/admin/providers" element={<AdminProviders />} />
        <Route
          path="/admin/providers/:providerId"
          element={<AdminProviderDetails />}
        />
        <Route path="/admin/users" element={<AdminUsers />} />
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Home />} />
    </Routes>
  );
}