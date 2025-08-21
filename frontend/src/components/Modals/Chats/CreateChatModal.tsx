import { useForm } from 'react-hook-form';
import styles from '../Modal.module.scss';
import type { CreateChat } from 'types/ChatsTypes';
import { useAppDispatch } from 'hooks/redux';
import { createChat } from 'store/reducers/chats/ActionCreators';

type Props = {
  isShow: boolean;
  chatsError?: string;
  isFetching: boolean;
  editCurrentModalOverlay: (value: string | null) => void;
};

type ConvertorKey = 'Сложность' | 'Вежливость' | 'Дружелюбность' | 'Жесткость' | 'Внимания к деталям' | 'Темп';

const SLIDER_ITEMS: ConvertorKey[] = [
  'Сложность',
  'Вежливость',
  'Дружелюбность',
  'Жесткость',
  'Внимания к деталям',
  'Темп',
];

const convertor: Record<ConvertorKey, keyof CreateChat> = {
  Сложность: 'difficulty',
  Вежливость: 'politeness',
  Дружелюбность: 'friendliness',
  Жесткость: 'rigidity',
  'Внимания к деталям': 'detail_orientation',
  Темп: 'pacing',
};

const PROGRAMMING_LANGUAGES = [
  'Python',
  'C++',
  'Java',
  'C#',
  'JavaScript',
  'Go',
  'SQL',
  'PHP',
  'Scratch',
  'Whitespace',
];

const PROGRESSION_TYPES = ['Арифметическая прогрессия', 'Геометрическая прогрессия'];

export const CreateChatModal = ({ isShow, editCurrentModalOverlay, isFetching, chatsError }: Props) => {
  const dispatch = useAppDispatch();
  const {
    register,
    handleSubmit,
    formState: { isSubmitting, errors },
  } = useForm<CreateChat>({
    defaultValues: {
      difficulty: 3,
      politeness: 3,
      friendliness: 3,
      rigidity: 3,
      detail_orientation: 3,
      pacing: 3,
      language: 0,
      progression_type: 0,
    },
  });

  const onSubmit = async (value: CreateChat) => {
    dispatch(createChat(value, () => editCurrentModalOverlay(null)));
  };

  return (
    <div className={styles.container} style={{ bottom: isShow ? '50%' : '150%' }}>
      <div className={styles.wrapper}>
        <button
          className={`${styles.close} ${isFetching || isSubmitting ? `${styles.close_disabled} fetching` : ''}`}
          type="button"
          disabled={isSubmitting || isFetching}
          onClick={() => editCurrentModalOverlay(null)}
        ></button>
        <h2 className={styles.title} style={{ fontSize: '40px' }}>
          Создание чата
        </h2>
        <form className={styles.form} onSubmit={handleSubmit(onSubmit)}>
          <div className={styles.input}>
            <input
              placeholder="Название чата"
              {...register('title', {
                required: 'Обязательное поле',
                minLength: {
                  value: 3,
                  message: 'Минимум 3 символа',
                },
              })}
            />
            {errors.title && <div className={styles.error}>{errors.title.message}</div>}
          </div>

          <div className={styles.input}>
            <textarea
              placeholder="Введите текст анкеты (опционально)..."
              rows={4}
              {...register('initial_context')}
              className={styles.textarea}
            />
            {errors.initial_context && <div className={styles.error}>{errors.initial_context.message}</div>}
          </div>

          {SLIDER_ITEMS.map((item, index) => (
            <div className={styles.slider} key={index}>
              <label>{item}</label>
              <input type="range" min={1} max={5} step={1} {...register(convertor[item])} />
              <div className={styles.slider_marks}>
                {[1, 2, 3, 4, 5].map((value) => (
                  <span key={value}>{value}</span>
                ))}
              </div>
            </div>
          ))}
          <div className={styles.input}>
            <div className={styles.slider_marks}>
              <span>Язык программирования</span>
            </div>
            <select {...register('language', { valueAsNumber: true })} className={styles.select}>
              {PROGRAMMING_LANGUAGES.map((lang, index) => (
                <option key={index} value={index}>
                  {lang}
                </option>
              ))}
            </select>
          </div>
          <div className={styles.input}>
            <div className={styles.slider_marks}>
              <span>Тип прогрессии шанса для ивентов</span>
            </div>
            <select {...register('progression_type', { valueAsNumber: true })} className={styles.select}>
              {PROGRESSION_TYPES.map((lang, index) => (
                <option key={index} value={index}>
                  {lang}
                </option>
              ))}
            </select>
          </div>
          <div className={`${styles.auth}`}>
            <button
              className={`${styles.button} ${isFetching ? `${styles.button_active} fetching` : ''}`}
              type="submit"
              disabled={isSubmitting || isFetching}
            >
              Создать чат
            </button>
            {chatsError && <div className={`${styles.auth_error} ${styles.error}`}>{chatsError}</div>}
          </div>
        </form>
      </div>
    </div>
  );
};
