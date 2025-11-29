import { useContext, useState } from "react";
import { AuthContext } from "../context/AuthContext";
import api from "../services/api";
import { Link, useNavigate } from "react-router-dom";

export default function Login() {
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handle = async (e) => {
    e.preventDefault();
    try {
      const res = await api.post("/auth/login", null, { params: { username, password } });
      login(res.data.access_token);
      navigate("/home");
    } catch (err) {
      alert("Login failed");
    }
  };

  return (
    <div className="h-screen flex items-center justify-center bg-gray-900 text-white">
      <form onSubmit={handle} className="bg-gray-800 p-8 rounded w-96">
        <h1 className="text-2xl mb-4">Login</h1>
        <input className="w-full p-2 mb-3 bg-gray-700 rounded" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="username" />
        <input className="w-full p-2 mb-3 bg-gray-700 rounded" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="password" />
        <button className="w-full bg-blue-600 p-2 rounded">Login</button>
        <p className="mt-3 text-sm text-gray-400">No account? <Link to="/register" className="text-blue-400">Register</Link></p>
      </form>
    </div>
  );
}
