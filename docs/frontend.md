# Frontend

React + TypeScript con Vite, servido en producción por nginx.

## Estructura

```
frontend/src/
├── assets/logo/      logo-placeholder.svg e index.ts
├── components/
│   ├── common/       Button, Input, Card, Modal, Table, Skeleton
│   └── layout/       Navbar, Sidebar, AppLayout, ProtectedRoute
├── context/          AuthContext.tsx
├── hooks/            useAuth.ts, useFetch.ts
├── pages/            Login, Inventory, Loans
├── services/         apiClients.ts, authService.ts, assetService.ts, loanService.ts
├── styles/           variables.css
└── types/            asset.ts, loan.ts, auth.ts
```

## Convenciones

- Alias `@/` apunta a `src/` (configurado en `tsconfig.app.json` y
  `vite.config.ts`).
- Las variables de entorno deben empezar con `VITE_`.
- Las URLs de los servicios se incrustan en tiempo de build, por eso van
  como `args` en `docker-compose.yml`.
- Los tipos de `src/types/` deben mantenerse sincronizados a mano con los
  schemas de Pydantic del backend.

## Logo

Para cambiar el logo, reemplazar `src/assets/logo/logo-placeholder.svg`
o cambiar el import en `src/assets/logo/index.ts`. Ningún componente
necesita modificarse.

## Responsive

- Breakpoints: 768px (tablet/móvil) y 480px (móvil pequeño).
- Sidebar: fija en escritorio, menú deslizante con overlay en móvil.
- Table: tabla en escritorio, tarjetas apiladas en móvil.
- Modal, formularios y botones se adaptan al ancho disponible.

## Skeleton Screens

`SkeletonTable` se muestra mientras cargan los datos. El hook `useFetch`
expone `data`, `isLoading`, `error` y `refetch`, y cada página decide
qué mostrar según el estado.

## Autenticación en el cliente

`AuthContext` guarda el usuario y recupera la sesión al recargar. El
token se guarda en `localStorage` y un interceptor de Axios lo adjunta a
cada petición. `ProtectedRoute` redirige a `/login` si no hay sesión y
acepta una lista opcional de roles permitidos.
