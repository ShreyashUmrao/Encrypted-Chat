import { useParams, useNavigate } from "react-router-dom";
import Chat from "./Chat";

export default function ChatPage() {
  const { roomId } = useParams();
  const navigate = useNavigate();

  return (
    <Chat 
      chatId={roomId}
      onBack={() => navigate("/home")}
    />
  );
}
