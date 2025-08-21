import type { IChat } from 'types/ChatsTypes';
import styles from './Chat.module.scss';
import type { FormEvent } from 'react';

type Props = {
  chat: IChat;
};

export const Chat = ({ chat }: Props) => {
  const handlerSendMessage = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
  };

  const inQueue = chat.queue_position >= 1;

  return (
    <div className={styles.container}>
      <div className={styles.top}>
        <span className={styles.top_title}>{chat.title}</span>
      </div>
      <div className={styles.content}>
        {inQueue && <span className={styles.content_queue}>Место в очереди: {chat.queue_position}</span>}
        <div className={`${styles.content__messages} ${inQueue ? 'blur' : ''}`}>
          {chat.messages.map((message) => message.content)}
        </div>
      </div>
      <form onSubmit={handlerSendMessage} className={styles.send}>
        <textarea />
        <button className={styles.send_button}>
          <span />
        </button>
      </form>
    </div>
  );
};
