import { ChatsList } from 'components/Chats/ChatsList/ChatsList';
import styles from './HomePage.module.scss';
import { useAppDispatch, useAppSelector } from 'hooks/redux';
import { useEffect } from 'react';
import { getChats, selectChat } from 'store/reducers/chats/ActionCreators';
import { Chat } from 'components/Chats/Chat/Chat';

type Props = { editCurrentModalOverlay: (value: string | null) => void };

export const HomePage = ({ editCurrentModalOverlay }: Props) => {
  const { chats, selectedChat } = useAppSelector((state) => state.chatsReducer);
  const dispatch = useAppDispatch();

  useEffect(() => {
    dispatch(getChats());
  }, []);

  return (
    <div className={styles.container}>
      <ChatsList
        selectChat={(id: number) => dispatch(selectChat(id))}
        editCurrentModalOverlay={editCurrentModalOverlay}
        chats={chats}
      />
      <Chat chat={selectedChat} />
    </div>
  );
};
