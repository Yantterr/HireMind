import type { TChats } from 'types/ChatsTypes';
import styles from './ChatsList.module.scss';

type Props = {
  chats: TChats;
  selectChat: (id: number) => void;
  editCurrentModalOverlay: (value: string | null) => void;
};

export const ChatsList = ({ chats, selectChat, editCurrentModalOverlay }: Props) => {
  return (
    <div className={styles.container}>
      <div className={`${styles.wrapper}`}>
        {chats.map((chat) => {
          const dateObject = new Date(chat.updated_at);
          return (
            <div className={styles.chat} onClick={() => selectChat(chat.id)} key={chat.id}>
              <div className={styles.chat_title}>{chat.title}</div>
              <div className={styles.chat_update}>
                {dateObject.getDay().toString().padStart(2, '0')}.{dateObject.getMonth().toString().padStart(2, '0')}.
                {dateObject.getFullYear()}
              </div>
            </div>
          );
        })}
        <button onClick={() => editCurrentModalOverlay('createChat')} className={styles.button}></button>
      </div>
    </div>
  );
};
