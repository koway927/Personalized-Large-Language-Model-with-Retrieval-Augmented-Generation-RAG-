import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { signInWithEmailAndPassword } from "firebase/auth";
import { auth } from "../backend/secret/firebase";

function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleLogin = async () => {
    if (email.trim() === "" || password.trim() === "") {
      alert("Please enter correct email address and password");
      return;
    }

    try {
      // Firebase Client SDK login
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      const idToken = await userCredential.user.getIdToken();

      // Send ID token to backend
      const response = await fetch("http://127.0.0.1:5000/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id_token: idToken }),
      });

      const data = await response.json();
      if (response.ok) {
        alert("Login Successful!");
        localStorage.setItem("user", JSON.stringify({ email: data.email, user_id: data.user_id, id_token: idToken }));
        console.error("localStorage",localStorage.getItem("user"));
        navigate("/chat");
      } else {
        alert(`Error: ${data.message}`);
      }
    } catch (error) {
      console.error("Error during login:", error);
      alert("An error occurred. Please try again.");
    }
  };

  return (
    <div className="min-h-screen flex justify-center items-start pt-24 bg-gray-100">
      <div className="bg-white shadow-lg rounded-lg p-8 w-full max-w-md">
        <h2 className="text-2xl font-bold mb-6 text-center">Sign In</h2>
        <div className="space-y-4">
          <input
            type="email"
            className="w-full px-4 py-2 border border-gray-300 rounded"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <input
            type="password"
            className="w-full px-4 py-2 border border-gray-300 rounded"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button
            onClick={handleLogin}
            className="w-full py-2 bg-black text-white rounded hover:bg-gray"
          >
            Sign In
          </button>
          <button
            onClick={() => navigate("/signup")}
            className="w-full py-2 bg-gray-300 text-black rounded hover:bg-gray-400 mt-4"
          >
            Sign Up
          </button>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;