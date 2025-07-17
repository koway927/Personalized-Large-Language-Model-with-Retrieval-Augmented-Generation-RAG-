import React from "react";
import { NavLink, useNavigate } from "react-router-dom";

function NavBar() {
  const navigate = useNavigate();
  const user = localStorage.getItem("user");

  const linkClass =
    "px-4 py-2 rounded hover:bg-blue-100 transition text-sm font-medium";

  const activeClass = "bg-black text-white";

  const handleLogout = async () => {
    const user = JSON.parse(localStorage.getItem("user"));
    const idToken = user?.id_token;
    if (!idToken) {
      alert("No user logged in");
      return;
    }
    try {
      const response = await fetch("http://127.0.0.1:5000/api/logoff", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id_token: idToken }),
      });
  
      const data = await response.json();
      if (response.ok) {
        alert("Logoff Successful!");
        localStorage.removeItem("user");
        navigate("/login");
      } else {
        alert(`Error: ${data.message}`);
      }
    } catch (error) {
      console.error("Error during logoff:", error);
      alert("An error occurred. Please try again.");
    }
  };

  return (
    <nav className="bg-white shadow p-4 flex justify-end gap-4">
      {!user && (
        <NavLink
          to="/login"
          className={({ isActive }) =>
            `${linkClass} ${isActive ? activeClass : ""}`
          }
        >
          Login
        </NavLink>
      )}
      <NavLink
        to="/chat"
        className={({ isActive }) =>
          `${linkClass} ${isActive ? activeClass : ""}`
        }
      >
        Chat
      </NavLink>
      <NavLink
        to="/profile"
        className={({ isActive }) =>
          `${linkClass} ${isActive ? activeClass : ""}`
        }
      >
        Account
      </NavLink>

      {user && (
        <button
          onClick={handleLogout}
          className={linkClass}
        >
          Log out
        </button>
      )}
    </nav>
  );
}

export default NavBar;
