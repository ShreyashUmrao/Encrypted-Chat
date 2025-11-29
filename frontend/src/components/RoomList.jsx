import { useEffect, useState } from "react";
import api from "../services/api";

export default function RoomList({ token, onSelectRoom }) {
  const [rooms, setRooms] = useState([]);
  const [newRoom, setNewRoom] = useState("");

  const load = async () => {
    try {
      const res = await api.get("/rooms");
      setRooms(res.data || []);
    } catch (e) {
      console.warn("failed to load rooms", e);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const createRoom = async () => {
    if (!newRoom.trim()) return;
    try {
      await api.post("/rooms", null, { params: { name: newRoom } });
      setNewRoom("");
      load();
    } catch (e) {
      alert("Create failed");
    }
  };

  return (
    <div className="w-64 p-3 flex flex-col gap-3 panel">
      <h2 className="text-lg font-semibold">Rooms</h2>
      <div className="flex gap-2">
        <input className="flex-1 p-2 bg-gray-800 rounded placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500" value={newRoom} onChange={(e) => setNewRoom(e.target.value)} placeholder="new room" />
        <button onClick={createRoom} className="px-3 bg-blue-600 rounded hover:bg-blue-700">+</button>
      </div>

      <div className="overflow-y-auto space-y-2">
        {rooms.map((r) => (
          <div key={r.id} className="p-2 mt-2 bg-gray-800 rounded hover:bg-gray-700 cursor-pointer flex items-center gap-3" onClick={() => onSelectRoom(r.name)}>
            <div className="avatar-initials">{(r.name||"?").charAt(0).toUpperCase()}</div>
            <div className="font-medium">{r.name}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
