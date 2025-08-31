import type { IChat } from 'types/ChatsTypes';
import styles from './Chat.module.scss';
import { useState, type FormEvent } from 'react';
import { Message } from '../Message/Message';
import { useAppDispatch } from 'hooks/redux';
import { sendMessage } from 'store/reducers/chats/ActionCreators';

type Props = {
  chat: IChat;
};

export const Chat = ({ chat }: Props) => {
  const dispatch = useAppDispatch();
  const [message, setMessage] = useState('');
  const isFetching = chat.queue_position > 0;

  const handlerSendMessage = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    dispatch(sendMessage(message));
    setMessage('');
  };

  return (
    <div className={styles.container}>
      <div className={styles.top}>
        <span className={styles.top_title}>{chat.title}</span>
      </div>
      <div className={styles.content}>
        {isFetching && <span className={styles.content_queue}>Место в очереди: {chat.queue_position}</span>}
        <div className={`${styles.content__messages} ${isFetching ? 'blur' : ''}`}>
          {chat.messages.map((message) => (
            <Message role={message.role} date={message.created_at} key={message.id} content={message.content} />
          ))}
        </div>
      </div>
      <form onSubmit={handlerSendMessage} className={`${styles.send} ${isFetching ? 'blur' : ''}`}>
        <textarea placeholder="Сообщение" value={message} onChange={(e) => setMessage(e.target.value)} />
        <button className={styles.send_button}>
          <span />
        </button>
      </form>
    </div>
  );
};
