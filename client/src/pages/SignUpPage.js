import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { auth } from "../backend/secret/firebase";
import { signInWithEmailAndPassword } from "firebase/auth";
function SignUpPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleSignUp = async () => {
    if (email.trim() === "" || password.trim() === "") {
      alert("Please fill in all fields");
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:5000/api/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password}),
      });

      const data = await response.json();
      if (response.ok) {
        alert("Sign-Up Successful! Redirecting to your profile...");
        // Navigate to ProfilePage and pass user data
        // Firebase Client SDK login
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        const idToken = await userCredential.user.getIdToken();
  
        const loginresponse = await fetch("http://127.0.0.1:5000/api/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ id_token: idToken }),
        });
        if (loginresponse.ok) {
          console.log("Login response", loginresponse);
          localStorage.setItem("user", JSON.stringify({ email: email, user_id: data.user_id, id_token: idToken }));
          console.error("localStorage",localStorage.getItem("user"));
          navigate("/profile");
        } else {
          alert(`Error: ${data.message}`);
        }
      } else {
        alert(`Error: ${data.message}`);
      }
    } catch (error) {
      console.error("Error during sign-up:", error);
      alert("An error occurred. Please try again.");
    }
  };

  return (
    <div className="min-h-screen flex justify-center items-start pt-24 bg-gray-100">
      <div className="bg-white shadow-lg rounded-lg p-8 w-full max-w-md">
        <h2 className="text-2xl font-bold mb-6 text-center">Sign Up</h2>
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
            onClick={handleSignUp}
            className="w-full py-2 bg-black text-white rounded hover:bg-gray"
          >
            Sign Up
          </button>
        </div>
      </div>
    </div>
  );
}

export default SignUpPage;