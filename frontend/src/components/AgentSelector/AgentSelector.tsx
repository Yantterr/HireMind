import { Backdrop, Box, Button, CircularProgress, Stack, Typography } from '@mui/material';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

type Agent = {
  id: string;
  name: string;
  description: string;
};

const agents: Agent[] = [
  {
    description: 'Жесткий мужик со своими приоритетами. Не любит когда мямлят и зумеров.',
    id: 'agent1',
    name: 'Начальник завода',
  },
  {
    description: 'Краткое описание агента 2',
    id: 'agent2',
    name: 'Агент 2',
  },
  {
    description: 'Краткое описание агента 3',
    id: 'agent3',
    name: 'Агент 3',
  },
  {
    description: 'Краткое описание агента 4',
    id: 'agent4',
    name: 'Агент 4',
  },
  {
    description: 'Краткое описание агента 5',
    id: 'agent5',
    name: 'Агент 5',
  },
  {
    description: 'Краткое описание агента 6',
    id: 'agent6',
    name: 'Агент 6',
  },
  {
    description: 'Краткое описание агента 7',
    id: 'agent7',
    name: 'Агент 7',
  },
  {
    description: 'Краткое описание агента 8',
    id: 'agent8',
    name: 'Агент 8',
  },
  {
    description: 'Краткое описание агента 9',
    id: 'agent9',
    name: 'Агент 9',
  },
  {
    description: 'Краткое описание агента 10',
    id: 'agent10',
    name: 'Агент 10',
  },
];

function AgentSelector() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleManualCreate = () => {
    navigate('/chat/new'); // Путь к странице создания агента
  };

  const handleSelectAgent = async (agentId: string) => {
    console.log(agentId);
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
    }, 5000);
  };

  return (
    <Box sx={{ margin: '20px 4px', maxWidth: 600 }}>
      <Typography variant="h6" gutterBottom>
        Выберите агента
      </Typography>
      <Stack spacing={2}>
        <Button
          variant="outlined"
          onClick={handleManualCreate}
          sx={{ justifyContent: 'flex-start', padding: '16px 8px', textAlign: 'left' }}
          disabled={loading}
        >
          <Box>
            <Typography variant="subtitle1">Ручное создание агента</Typography>
            <Typography variant="body2" color="text.secondary">
              Создайте агента вручную с нуля
            </Typography>
          </Box>
        </Button>

        {agents.map((agent) => (
          <Button
            key={agent.id}
            variant="outlined"
            onClick={() => handleSelectAgent(agent.id)}
            sx={{ justifyContent: 'flex-start', padding: '16px 8px', textAlign: 'left' }}
            disabled={loading}
          >
            <Box>
              <Typography variant="subtitle1">{agent.name}</Typography>
              <Typography variant="body2" color="text.secondary">
                {agent.description}
              </Typography>
            </Box>
          </Button>
        ))}
      </Stack>

      <Backdrop sx={{ color: '#fff', zIndex: (theme) => theme.zIndex.drawer + 1 }} open={loading}>
        <CircularProgress color="inherit" />
      </Backdrop>
    </Box>
  );
}

export default AgentSelector;
