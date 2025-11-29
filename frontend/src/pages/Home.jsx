import { useState, useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import RoomsPanel from "../components/RoomsPanel";
import { useNavigate } from "react-router-dom";

export default function Home() {
  const { logout } = useContext(AuthContext);
  const navigate = useNavigate();

  return (
    <div className="h-screen bg-gray-900 text-white flex">
      <div className="flex-1 flex flex-col">
        <header className="p-4 bg-gradient-to-r from-gray-800 to-gray-900 flex items-center justify-between panel">
          <div>
            <h1 className="text-xl font-semibold">Encrypted Chat</h1>
            <div className="text-sm text-gray-400">Welcome — pick or join a room</div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={logout}
              className="px-3 py-1 rounded bg-red-600 hover:bg-red-700"
            >
              Logout
            </button>
          </div>
        </header>

        <main className="flex-1">
          <div className="h-full flex items-center justify-center text-gray-400">
            <div className="max-w-md text-center panel p-6">
              <h2 className="text-2xl mb-2">Pick a room to start chatting</h2>
              <p className="text-gray-300">Rooms are listed on the right — search or click one to auto-join.</p>
            </div>
          </div>
        </main>
      </div>

      <aside className="w-80 border-l border-gray-800">
        <RoomsPanel
          onSelectRoom={(roomName) => navigate(`/chat/${roomName}`)}
        />
      </aside>
    </div>
  );
}
