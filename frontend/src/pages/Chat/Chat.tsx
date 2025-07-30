import ChatForm from 'components/ChatForm/ChatForm';
import UnknownChat from 'components/UnknownChat/UnknownChat';
import { useParams } from 'react-router-dom';

function Chat() {
  const { chatId } = useParams();
  if (chatId === undefined) return <UnknownChat chatId={chatId} />;

  return <ChatForm chatId={chatId} />;
}

export default Chat;
