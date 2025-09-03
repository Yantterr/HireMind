import { useState, useEffect, useRef, type FormEvent } from 'react';
import type { IChat } from 'types/ChatsTypes';
import styles from './Chat.module.scss';
import { chatsAPI } from 'api/api';
import { useAppDispatch } from 'hooks/redux';
import { sendMessage } from 'store/reducers/chats/ActionCreators';
import { Message } from '../Message/Message';

interface Props {
  chat: IChat;
  backToChats: () => void;
}

export const Chat = ({ chat, backToChats }: Props) => {
  const dispatch = useAppDispatch();
  const [message, setMessage] = useState('');
  const [isFetching, setIsFetching] = useState(chat.queue_position > 0);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const checkChatStatus = async () => {
    try {
      const response = await chatsAPI.getChat(chat.id);
      const updatedChat = response.data;

      setIsFetching(updatedChat.queue_position > 0);

      if (updatedChat.queue_position === 0 && intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    } catch (error) {
      console.error('Failed to check chat status:', error);
    }
  };

  useEffect(() => {
    if (chat.queue_position > 0 && !intervalRef.current) {
      intervalRef.current = setInterval(checkChatStatus, 5000);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [chat.id, chat.queue_position]);

  const handlerSendMessage = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    dispatch(sendMessage(message));
    setMessage('');

    if (!isFetching) {
      setIsFetching(true);
      setTimeout(() => {
        if (!intervalRef.current) {
          intervalRef.current = setInterval(checkChatStatus, 5000);
        }
      }, 2000);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.top}>
        <button onClick={backToChats} className={`${styles.send_button} ${styles.top_button}`}>
          <span />
        </button>
        <span className={styles.top_title}>{chat.title}</span>
      </div>
      {isFetching && <span className={styles.content_queue}>Место в очереди: {chat.queue_position}</span>}
      <div className={styles.content}>
        <div className={`${styles.content__messages} ${isFetching ? 'blur' : ''}`}>
          {chat.messages.map((message) => (
            <Message role={message.role} date={message.created_at} key={message.id} content={message.content} />
          ))}
        </div>
      </div>
      <form onSubmit={handlerSendMessage} className={styles.send}>
        <textarea
          className={isFetching ? styles.send_disabled : ''}
          placeholder="Сообщение"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          disabled={isFetching}
        />
        <button
          className={`${styles.send_button} ${isFetching ? `${styles.send_button_disabled} fetching` : ''}`}
          disabled={isFetching}
        >
          <span />
        </button>
      </form>
    </div>
  );
};
