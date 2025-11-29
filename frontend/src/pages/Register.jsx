import { useState } from "react";
import api from "../services/api";
import { Link, useNavigate } from "react-router-dom";

export default function Register() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handle = async (e) => {
    e.preventDefault();
    try {
      await api.post("/auth/register", null, { params: { username, password } });
      alert("Registered");
      navigate("/");
    } catch (err) {
      alert("Register failed");
    }
  };

  return (
    <div className="h-screen flex items-center justify-center bg-gray-900 text-white">
      <form onSubmit={handle} className="bg-gray-800 p-8 rounded w-96">
        <h1 className="text-2xl mb-4">Register</h1>
        <input className="w-full p-2 mb-3 bg-gray-700 rounded" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="username" />
        <input className="w-full p-2 mb-3 bg-gray-700 rounded" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="password" />
        <button className="w-full bg-green-600 p-2 rounded">Create</button>
        <p className="mt-3 text-sm text-gray-400">Have an account? <Link to="/" className="text-blue-400">Login</Link></p>
      </form>
    </div>
  );
}
