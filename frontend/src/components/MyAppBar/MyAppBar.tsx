import { AppBar, Avatar, Box, Container, Menu, MenuItem, Toolbar, Tooltip, Typography } from '@mui/material';
import IconButton from '@mui/material/IconButton';
import { useAppSelector } from 'hooks/redux';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const privateSettings = [
  { label: 'Профиль', url: '/profile' },
  { label: 'Выход', url: '/logout' },
  { label: 'Новый чат', url: '/new_chat' },
];

const anonymSettings = [
  { label: 'Войти', url: '/login' },
  { label: 'Зарегистрироваться', url: '/register' },
  { label: 'Новый чат', url: '/new_chat' },
];

export default function MyAppBar() {
  const { role } = useAppSelector((state) => state.authReducer.user);
  const navigate = useNavigate();

  const [anchorElUser, setAnchorElUser] = useState<null | HTMLElement>(null);

  const handleOpenUserMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorElUser(event.currentTarget);
  };

  const handleCloseUserMenu = (url: string) => {
    setAnchorElUser(null);
    navigate(url);
  };

  const settings = role === 'anonym' ? anonymSettings : privateSettings;

  return (
    <AppBar
      position="static"
      sx={{
        bgcolor: '#bf7dcb',
        zIndex: 'appBar',
      }}
    >
      <Container maxWidth="xl">
        <Toolbar
          disableGutters
          sx={{
            justifyContent: 'space-between',
          }}
        >
          <Box
            onClick={() => navigate('/')}
            sx={{
              alignItems: 'center',
              cursor: 'pointer',
              display: 'flex', // чтобы показать, что элемент кликабельный
            }}
          >
            <img
              src="/logo.png"
              alt="Несколько ромбов"
              style={{
                display: 'flex',
                // или другой подходящий размер
                height: '50px',

                marginRight: '8px',
                objectFit: 'contain',
                width: '50px',
                // для адаптивности можно использовать media queries или условный рендеринг
              }}
            />
            <Typography
              variant="h5"
              noWrap
              component="span"
              sx={{
                color: 'inherit',
                display: { md: 'flex', xs: 'flex' },
                flexGrow: 1,
                fontFamily: 'monospace',
                fontWeight: 700,
                letterSpacing: '.3rem',
                textDecoration: 'none',
              }}
            >
              nnchat.ru
            </Typography>
          </Box>
          <Box sx={{ flexGrow: 0 }}>
            <Tooltip title="Open settings">
              <IconButton onClick={handleOpenUserMenu} sx={{ p: 0 }}>
                <Avatar alt="Anon user" src="/static/images/avatar/2.jpg" />
              </IconButton>
            </Tooltip>
            <Menu
              sx={{ mt: '45px' }}
              id="menu-appbar"
              anchorEl={anchorElUser}
              anchorOrigin={{
                horizontal: 'right',
                vertical: 'top',
              }}
              keepMounted
              transformOrigin={{
                horizontal: 'right',
                vertical: 'top',
              }}
              open={Boolean(anchorElUser)}
              onClose={() => setAnchorElUser(null)}
            >
              {settings.map((setting) => (
                <MenuItem key={setting.url} onClick={() => handleCloseUserMenu(setting.url)}>
                  <Typography sx={{ textAlign: 'center' }}>{setting.label}</Typography>
                </MenuItem>
              ))}
            </Menu>
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
}
