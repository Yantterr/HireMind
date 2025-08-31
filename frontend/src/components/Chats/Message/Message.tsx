import type { MessageRoles } from 'types/ChatsTypes';
import styles from './Message.module.scss';

type Props = {
  content: string;
  date: string;
  role: MessageRoles;
};

export const Message = ({ content, date, role }: Props) => {
  const newDate = new Date(date);

  if (role === 'system') {
    return;
  }

  return (
    <div className={`${styles.message} ${role === 'assistant' ? styles.message_bot : ''}`}>
      <div className={`${styles.container} ${role === 'assistant' ? styles.message_bot : ''}`}>
        <div className={`${styles.message_content} ${role === 'assistant' ? styles.message_bot : ''}`}>{content}</div>
        <div className={`${styles.message_date} ${role === 'assistant' ? styles.message_bot : ''}`}>
          {newDate.getHours().toString().padStart(2, '0')}:{newDate.getMinutes().toString().padStart(2, '0')}
        </div>
      </div>
    </div>
  );
};
