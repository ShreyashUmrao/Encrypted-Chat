import { useEffect, useState, useContext } from "react";
import api from "../services/api";
import { AuthContext } from "../context/AuthContext";

export default function RoomsPanel({ onSelectRoom }) {
  const { token } = useContext(AuthContext);
  const [rooms, setRooms] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [newRoomName, setNewRoomName] = useState("");

  const loadRooms = async () => {
    setLoading(true);
    try {
      const res = await api.get("/rooms", { headers: { Authorization: `Bearer ${token}` } });
      setRooms(res.data || []);
    } catch (err) {
      console.error("Failed to load rooms", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRooms();
  }, []);

  const handleCreateRoom = async () => {
    if (!newRoomName.trim()) return;
    setCreating(true);
    try {
      await api.post("/rooms", null, {
        params: { name: newRoomName.trim() },
        headers: { Authorization: `Bearer ${token}` },
      });
      setNewRoomName("");
      await loadRooms();
    } catch (err) {
      console.error("Create room failed", err);
      alert("Failed to create room");
    } finally {
      setCreating(false);
    }
  };

  const handleClickRoom = async (room) => {
    try {
      await api.post(`/rooms/${room.id}/join`, null, {
        headers: { Authorization: `Bearer ${token}` },
      });
    } catch (err) {
      console.debug("join error (ignored):", err);
    }
    onSelectRoom(room.name);
  };

  const filtered = rooms.filter((r) => r.name.toLowerCase().includes(search.toLowerCase()));

  return (
    <div className="p-4 h-full flex flex-col gap-3 panel">
      <div className="mb-1">
        <input
          className="w-full p-2 rounded bg-gray-800 text-sm placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Search rooms..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <div className="mb-1 flex gap-2">
        <input
          className="flex-1 p-2 rounded bg-gray-800 text-sm placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="New room name"
          value={newRoomName}
          onChange={(e) => setNewRoomName(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter") handleCreateRoom(); }}
        />
        <button
          onClick={handleCreateRoom}
          className="px-3 py-1 bg-blue-600 rounded hover:bg-blue-700 disabled:opacity-50"
          disabled={creating}
        >
          {creating ? "..." : "Create"}
        </button>
      </div>

      <div className="text-xs text-gray-400 mb-2">{loading ? "Loading rooms..." : `${filtered.length} rooms`}</div>

      <div className="overflow-y-auto flex-1 space-y-2">
        {filtered.map((room) => (
          <button
            key={room.id}
            onClick={() => handleClickRoom(room)}
            className="w-full text-left p-3 rounded bg-gray-800 hover:bg-gray-700 flex items-center gap-3 msg-shadow"
          >
            <div className="avatar-initials">{(room.name || "?").charAt(0).toUpperCase()}</div>
            <div className="flex-1">
              <div className="font-medium">{room.name}</div>
              <div className="text-xs text-gray-400">{room.user_count ? `${room.user_count} members` : ""}</div>
            </div>
            <div className="text-xs text-gray-400">›</div>
          </button>
        ))}

        {!loading && filtered.length === 0 && (
          <div className="text-gray-500 text-sm mt-3">No rooms match your search.</div>
        )}
      </div>
    </div>
  );
}
